import time

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.resources import Resource

provider = TracerProvider(
    resource=Resource.create({
        "service.name": "portfolio-tracing-demo"
    })
)
provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("portfolio.tracing_demo")

with tracer.start_as_current_span("practice_login") as login_span:
    login_span.set_attribute("app.operation", "admin_login")
    login_span.set_attribute("app.simulated", True)

    with tracer.start_as_current_span("simulated_database"):
        time.sleep(0.1)

    with tracer.start_as_current_span("simulated_password"):
        time.sleep(0.15)

    login_span.set_attribute("app.login.outcome", "rejected")

    login_span.add_event(
        "credential_check_completed",
        {"app.login.outcome": "rejected"}
    )
    login_span.set_attribute("app.login.outcome", "rejected")

provider.shutdown()