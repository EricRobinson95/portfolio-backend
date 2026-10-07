import io
import json
import logging
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import NoOpTracerProvider, SpanKind, StatusCode

from app.core import tracing
from app.core.logging import RequestLoggingMiddleware, logger
from app.core.security_logging import security_logger
from app.dependencies.auth_service_dependencies import get_auth_service
from app.exceptions.exception_handlers import register_exception_handlers
from app.routers.auth_router import router
from app.services.auth_service import AuthService

from app.services import auth_service


@pytest.fixture
def span_exporter(monkeypatch):
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    monkeypatch.setattr(
        tracing.trace,
        "get_tracer",
        provider.get_tracer,
    )

    try:
        yield exporter
    finally:
        provider.shutdown()


@pytest.mark.parametrize(
    "error, expected_status",
    [
        (
            HTTPException(401, detail="private-test-message"),
            StatusCode.UNSET,
        ),
        (
            RuntimeError("private-test-message"),
            StatusCode.ERROR,
        ),
    ],
)
def test_exception_status_and_privacy(span_exporter, error, expected_status):
    with pytest.raises(type(error)) as caught:
        with tracing.operation_span("test.operation"):
            raise error

    assert caught.value is error

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1

    span = spans[0]
    assert span.status.status_code == expected_status
    assert "private-test-message" not in span.to_json()

    if expected_status == StatusCode.ERROR:
        assert span.attributes["error.type"] == "RuntimeError"

def test_database_failure_marks_parent_and_child(span_exporter):
    class FailingRepository:
        def get_by_username(self, username):
            raise RuntimeError("private-database-message")

    service = AuthService(FailingRepository())

    with pytest.raises(RuntimeError):
        service.authenticate("test-admin", "test-password")

    spans = {
        span.name: span
        for span in span_exporter.get_finished_spans()
    }

    assert set(spans) == {
        "admin.authenticate",
        "admin.lookup",
    }

    parent = spans["admin.authenticate"]
    child = spans["admin.lookup"]

    assert child.context.trace_id == parent.context.trace_id
    assert child.parent.span_id == parent.context.span_id

    for span in spans.values():
        assert span.status.status_code == StatusCode.ERROR
        assert "private-database-message" not in span.to_json()
        assert "test-password" not in span.to_json()


@pytest.mark.parametrize("password_valid", [False, True])
def test_login_spans_and_privacy(span_exporter, monkeypatch, password_valid):
    class FakeRepository:
        def get_by_username(self, username):
            return SimpleNamespace(
                username=username,
                password_hash="private-password-hash",
            )

    monkeypatch.setattr(
        auth_service,
        "verify_password",
        lambda password, password_hash: password_valid,
    )
    monkeypatch.setattr(
        auth_service,
        "create_access_token",
        lambda username: "private-test-token",
    )

    service = AuthService(FakeRepository())

    if password_valid:
        assert service.authenticate("private-admin", "private-password") == (
            "private-test-token"
        )
    else:
        with pytest.raises(HTTPException) as caught:
            service.authenticate("private-admin", "private-password")
        assert caught.value.status_code == 401

    spans = {
        span.name: span
        for span in span_exporter.get_finished_spans()
    }

    expected_names = {
        "admin.authenticate",
        "admin.lookup",
        "admin.verify_password",
    }
    if password_valid:
        expected_names.add("admin.create_token")

    assert set(spans) == expected_names

    parent = spans["admin.authenticate"]
    assert parent.attributes["app.login.outcome"] == (
        "success" if password_valid else "rejected"
    )

    for span in spans.values():
        assert span.status.status_code == StatusCode.UNSET

        if span is not parent:
            assert span.context.trace_id == parent.context.trace_id
            assert span.parent.span_id == parent.context.span_id

        for private_value in (
            "private-admin",
            "private-password",
            "private-password-hash",
            "private-test-token",
        ):
            assert private_value not in span.to_json()


@pytest.fixture
def request_logs():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    levels = [item.level for item in (logger, security_logger)]
    for item in (logger, security_logger):
        item.addHandler(handler)
        item.setLevel(logging.INFO)
    try:
        yield stream
    finally:
        for item, level in zip((logger, security_logger), levels):
            item.removeHandler(handler)
            item.setLevel(level)
        handler.close()


@pytest.mark.parametrize("outcome, status_code", [
    ("success", 200), ("rejected", 401), ("unknown_admin", 401), ("error", 500),
])
def test_http_login_trace_and_log_correlation(
    span_exporter, request_logs, monkeypatch, outcome, status_code,
):
    class FakeRepository:
        def get_by_username(self, username):
            if outcome == "error":
                raise RuntimeError("private-database-message")
            if outcome == "unknown_admin":
                return None
            return SimpleNamespace(username=username, password_hash="private-hash")

    monkeypatch.setattr(auth_service, "verify_password", lambda *_: outcome == "success")
    monkeypatch.setattr(auth_service, "create_access_token", lambda _: "private-token")
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api")
    app.add_middleware(RequestLoggingMiddleware)
    app.dependency_overrides[get_auth_service] = lambda: AuthService(FakeRepository())

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/auth/login?key=private-query", json={
            "username": "private-admin", "password": "private-password",
        }, headers={"Authorization": "Bearer private-header"})

    assert response.status_code == status_code
    spans = {span.name: span for span in span_exporter.get_finished_spans()}
    root = spans["POST /api/auth/login"]
    auth = spans["admin.authenticate"]
    assert root.kind == SpanKind.SERVER
    assert root.parent is None
    assert auth.parent.span_id == root.context.span_id
    assert all(span.context.trace_id == root.context.trace_id for span in spans.values())
    assert root.start_time <= auth.start_time <= auth.end_time <= root.end_time
    assert root.attributes["http.response.status_code"] == status_code
    assert root.attributes["http.route"] == "/api/auth/login"
    assert root.status.status_code == (
        StatusCode.ERROR if status_code == 500 else StatusCode.UNSET
    )

    events = [json.loads(line) for line in request_logs.getvalue().splitlines()]
    assert {event["event"] for event in events} == {"http_request", "security_event"}
    for event in events:
        assert event["trace_id"] == format(root.context.trace_id, "032x")
        assert event["span_id"] == format(root.context.span_id, "016x")
        assert event["request_id"] == response.headers["X-Request-ID"]
        assert event["request_id"] == root.attributes["app.request_id"]

    output = request_logs.getvalue() + "".join(span.to_json() for span in spans.values())
    for secret in (
        "private-admin", "private-password", "private-hash", "private-token",
        "private-query", "private-header", "private-database-message",
    ):
        assert secret not in output


@pytest.mark.parametrize("path, expected_name, status_code", [
    ("/items/private-item", "GET /items/{item_id}", 200),
    ("/private-missing-path", "GET", 404),
    ("/unavailable", "GET /unavailable", 503),
])
def test_http_span_uses_safe_route_and_response_status(
    span_exporter, request_logs, path, expected_name, status_code,
):
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/items/{item_id}")
    async def item(item_id: str):
        return {"ok": True}

    @app.get("/unavailable")
    async def unavailable():
        raise HTTPException(503, "private-error-message")

    with TestClient(app) as client:
        response = client.get(path + "?secret=private-query", headers={
            "Authorization": "Bearer private-header",
            "traceparent": "00-11111111111111111111111111111111-2222222222222222-01",
        })
        client.get("/items/another-private-item")

    assert response.status_code == status_code
    first, second = span_exporter.get_finished_spans()
    assert first.name == expected_name
    assert first.parent is None
    assert first.context.trace_id != int("1" * 32, 16)
    assert first.context.trace_id != second.context.trace_id
    assert first.status.status_code == (
        StatusCode.ERROR if status_code == 503 else StatusCode.UNSET
    )
    if status_code == 404:
        assert "http.route" not in first.attributes
    output = request_logs.getvalue() + first.to_json() + second.to_json()
    for secret in (
        "private-item", "private-missing-path", "private-query",
        "private-header", "private-error-message",
    ):
        assert secret not in output


def test_inactive_tracing_omits_ids_from_request_logs(request_logs, monkeypatch):
    monkeypatch.setattr(tracing.trace, "get_tracer", NoOpTracerProvider().get_tracer)
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        response = client.get("/health")

    event = json.loads(request_logs.getvalue())
    assert response.status_code == 200
    assert "trace_id" not in event
    assert "span_id" not in event
    assert event["request_id"] == response.headers["X-Request-ID"]


@pytest.mark.parametrize("nested", [False, True])
def test_included_router_prefixes_preserve_safe_route_pattern(
    span_exporter, request_logs, nested,
):
    items = APIRouter(prefix="/items")

    @items.get("/{item_id}")
    async def item(item_id: str):
        return {"ok": True}

    app = FastAPI()
    if nested:
        api = APIRouter(prefix="/api")
        api.include_router(items, prefix="/v1")
        app.include_router(api)
        prefix = "/api/v1"
    else:
        app.include_router(items, prefix="/api")
        prefix = "/api"
    app.add_middleware(RequestLoggingMiddleware)

    with TestClient(app) as client:
        response = client.get(prefix + "/items/private-item-id")

    assert response.status_code == 200
    span, = span_exporter.get_finished_spans()
    event = json.loads(request_logs.getvalue())
    pattern = prefix + "/items/{item_id}"
    assert span.name == "GET " + pattern
    assert span.attributes["http.route"] == pattern
    assert event["route"] == pattern
    assert "private-item-id" not in span.to_json() + request_logs.getvalue()
