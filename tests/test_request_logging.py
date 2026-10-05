import io
import json
import logging
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging import RequestLoggingMiddleware, logger
from app.exceptions.exception_handlers import register_exception_handlers


@pytest.fixture
def logging_client():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    previous_level = logger.level
    logger.setLevel(logging.INFO)

    app = FastAPI()
    register_exception_handlers(app)
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/items/{item_id}")
    async def read_item(item_id: str):
        return {"ok": True}

    @app.get("/failure")
    async def fail():
        raise RuntimeError("private-error-value")

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client, stream
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        handler.close()


def read_events(stream):
    return [
        json.loads(line)
        for line in stream.getvalue().splitlines()
    ]


def test_success_logs_request_and_matches_response_id(logging_client):
    client, stream = logging_client

    response = client.get("/items/123")
    event = read_events(stream)[0]

    assert response.status_code == 200
    assert event["status_code"] == 200
    assert event["route"] == "/items/{item_id}"
    assert event["duration_ms"] >= 0
    assert event["request_id"] == response.headers["X-Request-ID"]
    UUID(event["request_id"])


def test_logs_exclude_sensitive_request_values(logging_client):
    client, stream = logging_client

    client.get(
        "/items/private-item?token=private-query",
        headers={"Authorization": "Bearer private-token"},
    )

    output = stream.getvalue()
    assert "private-item" not in output
    assert "private-query" not in output
    assert "private-token" not in output


def test_unexpected_error_is_logged_without_exception_message(logging_client):
    client, stream = logging_client

    response = client.get("/failure")
    event = read_events(stream)[0]

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}
    assert event["level"] == "ERROR"
    assert event["error_type"] == "RuntimeError"
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert "private-error-value" not in stream.getvalue()


def test_missing_route_and_unique_request_ids(logging_client):
    client, stream = logging_client

    first = client.get("/missing-private-path")
    second = client.get("/items/123")
    events = read_events(stream)

    assert first.status_code == 404
    assert events[0]["route"] == "<unmatched>"
    assert "missing-private-path" not in stream.getvalue()
    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]
    assert len(events) == 2