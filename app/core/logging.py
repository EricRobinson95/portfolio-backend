import json
import logging
import sys
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.security_logging import configure_security_logging, log_security_event


logger = logging.getLogger("portfolio.requests")


def configure_logging() -> None:
    configure_security_logging()
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

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
            route_pattern = getattr(route, "path", "<unmatched>")

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
                )
            elif status_code in (401, 403):
                log_security_event(
                    action="access_denied", outcome="rejected", source="http",
                    request_id=request_id, status_code=status_code,
                    reason="unauthorized_or_forbidden",
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

            logger.log(
                logging.ERROR if status_code >= 500 else logging.INFO,
                json.dumps(event),
            )
