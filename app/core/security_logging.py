import json
import logging
import sys
from datetime import datetime, timezone
from typing import Literal

from app.core.tracing import trace_log_fields

security_logger = logging.getLogger("portfolio.security")


def configure_security_logging() -> None:
    if not security_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        security_logger.addHandler(handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False


def log_security_event(
    *,
    action: Literal["admin_login", "access_denied", "admin_password_reset"],
    outcome: Literal["started", "success", "rejected", "error"],
    source: Literal["http", "operator_script"],
    request_id: str | None = None,
    operation_id: str | None = None,
    reason: str | None = None,
    status_code: int | None = None,
    client_ip: str | None = None,
    client_ip_source: Literal["peer", "alb", "cloudflare"] | None = None,
) -> None:
    # Callers supply fixed reason codes, never credentials or exception text.
    level = (
        logging.ERROR if outcome == "error"
        else logging.WARNING if outcome == "rejected"
        else logging.INFO
    )
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": logging.getLevelName(level),
        "service": "portfolio-backend",
        "event": "security_event",
        "action": action,
        "outcome": outcome,
        "source": source,
    }
    for key, value in {
        "request_id": request_id,
        "operation_id": operation_id,
        "reason": reason,
        "status_code": status_code,
        "client_ip": client_ip,
        "client_ip_source": client_ip_source,
    }.items():
        if value is not None:
            event[key] = value
    event.update(trace_log_fields())
    security_logger.log(level, json.dumps(event))
