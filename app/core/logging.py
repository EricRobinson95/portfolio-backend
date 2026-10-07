import json
import logging
import sys
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from opentelemetry.context import Context
from opentelemetry.trace import Span, SpanKind, Status, StatusCode
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.client_ip import ClientIPResolver
from app.core.security_logging import configure_security_logging, log_security_event
from app.core.tracing import operation_span, trace_log_fields


logger = logging.getLogger("portfolio.requests")


def _route_pattern(scope: Scope) -> str:
    # FastAPI 0.141 keeps the original APIRoute in scope["route"]. Its
    # effective context includes prefixes from every included router.
    effective_route = scope.get("fastapi", {}).get("effective_route_context")
    route = effective_route or scope.get("route")
    return (
        getattr(route, "path_format", None)
        or getattr(route, "path", None)
        or "<unmatched>"
    )


def configure_logging() -> None:
    configure_security_logging()
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp, trusted_proxy_cidrs: tuple[str, ...] = ()) -> None:
        self.app = app
        self.client_ip_resolver = ClientIPResolver(trusted_proxy_cidrs)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

        # Start a backend trace without trusting visitor-supplied trace headers.
        with operation_span(
            "HTTP",
            kind=SpanKind.SERVER,
            instrumentation_scope="portfolio.http",
            context=Context(),
            # Only classify fixed endpoints here; never attach actual URL paths.
            attributes={
                "app.health_check": scope.get("path") == "/health",
                "app.operation": (
                    "admin_login" if scope["method"] == "POST"
                    and scope.get("path") == "/api/auth/login" else "http_request"
                ),
            },
        ) as span:
            await self._handle_request(scope, receive, send, request_id, span)

    async def _handle_request(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        request_id: str,
        span: Span,
    ) -> None:
        started = perf_counter()
        status_code = 500
        error_type = None

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = [
                    (name, value)
                    for name, value in message.get("headers", [])
                    if name.lower() != b"x-request-id"
                ]
                headers.append(
                    (b"x-request-id", request_id.encode("ascii"))
                )
                message = {**message, "headers": headers}

            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception as exc:
            error_type = type(exc).__name__
            raise
        finally:
            route = scope.get("route")
            route_pattern = _route_pattern(scope)
            client_ip, client_ip_source = self.client_ip_resolver.resolve(scope)

            method = scope["method"]
            if method not in {
                "GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT",
                "OPTIONS", "TRACE", "PATCH",
            }:
                method = "_OTHER"
            span.update_name(
                f"{method} {route_pattern}" if route else method
            )
            span.set_attribute("http.request.method", method)
            span.set_attribute("http.response.status_code", status_code)
            span.set_attribute("app.request_id", request_id)
            if route:
                span.set_attribute("http.route", route_pattern)
            if status_code >= 500 or error_type:
                span.set_status(Status(StatusCode.ERROR))
                span.set_attribute("error.type", error_type or str(status_code))

            if (
                scope["method"] == "POST"
                and getattr(route, "endpoint", None) is not None
                and getattr(route.endpoint, "security_action", None) == "admin_login"
            ):
                outcome, reason = {
                    200: ("success", None),
                    401: ("rejected", "invalid_credentials"),
                    422: ("rejected", "invalid_request"),
                }.get(status_code, ("error", "authentication_error"))
                log_security_event(
                    action="admin_login", outcome=outcome, source="http",
                    request_id=request_id, status_code=status_code, reason=reason,
                    client_ip=client_ip, client_ip_source=client_ip_source,
                )
            elif status_code in (401, 403):
                log_security_event(
                    action="access_denied", outcome="rejected", source="http",
                    request_id=request_id, status_code=status_code,
                    reason="unauthorized_or_forbidden",
                    client_ip=client_ip, client_ip_source=client_ip_source,
                )

            event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "ERROR" if status_code >= 500 else "INFO",
                "service": "portfolio-backend",
                "event": "http_request",
                "request_id": request_id,
                "method": scope["method"],
                "route": route_pattern,
                "status_code": status_code,
                "duration_ms": round(
                    (perf_counter() - started) * 1000, 2
                ),
            }

            if error_type:
                event["error_type"] = error_type

            event.update(trace_log_fields())

            logger.log(
                logging.ERROR if status_code >= 500 else logging.INFO,
                json.dumps(event),
            )
