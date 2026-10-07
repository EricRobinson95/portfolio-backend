import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.context import Context
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ParentBased
from opentelemetry.trace import SpanKind

from app.core import tracing
from app.core.logging import RequestLoggingMiddleware


@pytest.fixture
def configured_provider(monkeypatch):
    # Do not replace the process-global SDK singleton used by unrelated tests.
    monkeypatch.setattr(tracing, "_provider", None)
    monkeypatch.setattr(tracing.trace, "set_tracer_provider", lambda provider: None)
    monkeypatch.setattr(
        tracing.trace, "get_tracer",
        lambda name: tracing._provider.get_tracer(name),
    )
    yield
    if tracing._provider is not None:
        tracing._provider.shutdown()


def test_otlp_exports_real_protobuf_and_keeps_private_values_out(configured_provider):
    received = []

    class Receiver(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            message = ExportTraceServiceRequest()
            message.ParseFromString(body)
            received.append((self.path, self.headers["Content-Type"], message))
            self.send_response(200)
            self.send_header("Content-Type", "application/x-protobuf")
            self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        provider = tracing.configure_tracing(
            True, exporter="otlp", environment="production", sample_ratio=0,
            endpoint=f"http://127.0.0.1:{server.server_port}/v1/traces",
        )
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/health")
        def health():
            return {"status": "ok"}

        @app.post("/api/auth/login")
        def login():
            with tracing.operation_span("admin.authenticate") as parent:
                with tracing.operation_span("admin.lookup"):
                    pass
                with tracing.operation_span("admin.verify_password"):
                    pass
                parent.set_attribute("app.login.outcome", "rejected")
            return {"ok": True}

        @app.get("/items/{item_id}")
        def item(item_id: str):
            return {"ok": True}

        with TestClient(app) as client:
            client.get("/health")
            client.get("/items/private-id?key=private-query")
            client.post("/api/auth/login?key=private-query", json={
                "username": "private-user", "password": "private-password",
            }, headers={"Authorization": "Bearer private-token"})
        assert provider.force_flush(timeout_millis=5000)
        assert received
        all_spans = []
        for path, content_type, message in received:
            assert path == "/v1/traces"
            assert content_type == "application/x-protobuf"
            for resource_spans in message.resource_spans:
                resource = {item.key: item.value.string_value for item in resource_spans.resource.attributes}
                assert resource["service.name"] == "portfolio-backend"
                assert resource["deployment.environment.name"] == "production"
                for scope_spans in resource_spans.scope_spans:
                    all_spans.extend(scope_spans.spans)
            for secret in ("private-id", "private-query", "private-user", "private-password", "private-token"):
                assert secret not in str(message)
        names = {span.name for span in all_spans}
        assert names == {
            "POST /api/auth/login", "admin.authenticate",
            "admin.lookup", "admin.verify_password",
        }
        assert len(all_spans) == 4
        root = next(span for span in all_spans if span.name == "POST /api/auth/login")
        auth = next(span for span in all_spans if span.name == "admin.authenticate")
        assert not root.parent_span_id
        assert auth.parent_span_id == root.span_id
        assert {span.trace_id for span in all_spans} == {root.trace_id}
        assert abs(int.from_bytes(root.trace_id[:4], "big") - int(time.time())) < 5
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize("ratio, expected", [(0, 0), (1, 1)])
def test_sampling_inherits_parent_and_excludes_health(ratio, expected):
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=ParentBased(tracing.RequestSampler(ratio)))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")
    try:
        with tracer.start_as_current_span("HTTP", context=Context(), attributes={"app.health_check": True}):
            with tracer.start_as_current_span("health.child"):
                pass
        assert not exporter.get_finished_spans()
        with tracer.start_as_current_span("HTTP", context=Context(), attributes={"app.operation": "admin_login"}) as root:
            with tracer.start_as_current_span("admin.lookup") as child:
                assert child.is_recording()
                assert child.get_span_context().trace_id == root.get_span_context().trace_id
        assert len(exporter.get_finished_spans()) == 2
        exporter.clear()
        with tracer.start_as_current_span("ordinary", context=Context()):
            pass
        assert len(exporter.get_finished_spans()) == expected
    finally:
        provider.shutdown()


def test_batch_export_does_not_block_request_thread(configured_provider, monkeypatch):
    entered = threading.Event()
    release = threading.Event()
    export_threads = []

    class SlowExporter(SpanExporter):
        def export(self, spans):
            export_threads.append(threading.get_ident())
            entered.set()
            release.wait(timeout=5)
            return SpanExportResult.SUCCESS

    monkeypatch.setattr(tracing, "OTLPSpanExporter", lambda **kwargs: SlowExporter())
    provider = tracing.configure_tracing(True, exporter="otlp", sample_ratio=1)
    assert isinstance(provider._active_span_processor._span_processors[0], BatchSpanProcessor)
    try:
        with tracing.operation_span("first", kind=SpanKind.SERVER):
            pass
        assert entered.wait(timeout=3)
        # Export is still blocked; producing a second span must return immediately.
        with tracing.operation_span("second") as span:
            assert span.is_recording()
        assert export_threads[0] != threading.get_ident()
    finally:
        release.set()
        assert provider.force_flush(timeout_millis=5000)


def test_disabled_tracing_does_not_create_exporter(configured_provider, monkeypatch):
    def unexpected(**kwargs):
        pytest.fail("Exporter created while tracing disabled")
    monkeypatch.setattr(tracing, "OTLPSpanExporter", unexpected)
    assert tracing.configure_tracing(False, exporter="otlp") is None
    assert tracing._provider is None
