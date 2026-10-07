from contextlib import contextmanager

from fastapi import HTTPException
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


_provider: TracerProvider | None = None


def configure_tracing(enabled: bool) -> TracerProvider | None:
    global _provider

    if not enabled:
        return None

    if _provider is None:
        _provider = TracerProvider(
            resource=Resource.create({
                "service.name": "portfolio-backend",
            })
        )
        _provider.add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter())
        )
        trace.set_tracer_provider(_provider)

    return _provider


@contextmanager
def operation_span(
    name: str,
    *,
    kind: SpanKind = SpanKind.INTERNAL,
    instrumentation_scope: str = "portfolio.auth",
    context: Context | None = None,
):
    tracer = trace.get_tracer(instrumentation_scope)

    with tracer.start_as_current_span(
        name,
        kind=kind,
        context=context,
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


def trace_log_fields() -> dict[str, str]:
    """Link a log to the current span; omit IDs when tracing is inactive."""
    context = trace.get_current_span().get_span_context()
    if not context.is_valid:
        return {}
    return {
        "trace_id": format(context.trace_id, "032x"),
        "span_id": format(context.span_id, "016x"),
    }
