from contextlib import contextmanager

from fastapi import HTTPException
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF, ALWAYS_ON, ParentBased, Sampler, TraceIdRatioBased,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)


_provider: TracerProvider | None = None


class RequestSampler(Sampler):
    """Keep login traces, exclude probes, and sample other backend requests."""

    def __init__(self, ratio: float):
        self.default = TraceIdRatioBased(ratio)

    def should_sample(self, parent_context, trace_id, name, kind=None,
                      attributes=None, links=None, trace_state=None):
        attributes = attributes or {}
        sampler = self.default
        if attributes.get("app.health_check"):
            sampler = ALWAYS_OFF
        elif attributes.get("app.operation") == "admin_login":
            sampler = ALWAYS_ON
        return sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links, trace_state,
        )

    def get_description(self):
        return "RequestSampler(health=off, admin_login=on, others=ratio)"


def configure_tracing(
    enabled: bool,
    *,
    exporter: str = "console",
    endpoint: str = "http://portfolio-otel:4318/v1/traces",
    sample_ratio: float = 0.1,
    environment: str = "development",
) -> TracerProvider | None:
    global _provider

    if not enabled:
        return None

    if _provider is None:
        # Validate before installing a provider so startup failures can be retried.
        if exporter not in {"console", "otlp"}:
            raise ValueError("Unsupported tracing exporter")
        if exporter == "otlp":
            processor = BatchSpanProcessor(
                OTLPSpanExporter(endpoint=endpoint, timeout=3),
                max_queue_size=2048,
                max_export_batch_size=128,
                schedule_delay_millis=1000,
            )
        else:
            processor = SimpleSpanProcessor(ConsoleSpanExporter())
        _provider = TracerProvider(
            resource=Resource.create({
                "service.name": "portfolio-backend",
                "deployment.environment.name": environment,
            }),
            sampler=ParentBased(RequestSampler(sample_ratio)),
            id_generator=AwsXRayIdGenerator(),
        )
        _provider.add_span_processor(processor)
        trace.set_tracer_provider(_provider)

    return _provider


@contextmanager
def operation_span(
    name: str,
    *,
    kind: SpanKind = SpanKind.INTERNAL,
    instrumentation_scope: str = "portfolio.auth",
    context: Context | None = None,
    attributes: dict | None = None,
):
    tracer = trace.get_tracer(instrumentation_scope)

    with tracer.start_as_current_span(
        name,
        kind=kind,
        context=context,
        attributes=attributes,
        record_exception=False,
        set_status_on_exception=False,
    ) as span:
        try:
            yield span
        except Exception as exc:
            expected_rejection = (
                isinstance(exc, HTTPException)
                and exc.status_code < 500
            )

            if not expected_rejection:
                span.set_attribute("error.type", type(exc).__name__)
                span.set_status(Status(StatusCode.ERROR))

            raise


def trace_log_fields() -> dict[str, str | bool]:
    """Link a log to the current span; omit IDs when tracing is inactive."""
    context = trace.get_current_span().get_span_context()
    if not context.is_valid:
        return {}
    trace_id = format(context.trace_id, "032x")
    return {
        "trace_id": trace_id,
        "xray_trace_id": f"1-{trace_id[:8]}-{trace_id[8:]}",
        "span_id": format(context.span_id, "016x"),
        "trace_sampled": bool(context.trace_flags.sampled),
    }
