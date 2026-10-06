import io
import json
import logging
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging import RequestLoggingMiddleware, logger
from app.core.security_logging import security_logger
from app.dependencies.auth_service_dependencies import get_auth_service
from app.exceptions.exception_handlers import register_exception_handlers
from app.routers.auth_router import router
from app.services.auth_service import AuthService
from scripts import reset_admin_password as reset_script


@pytest.fixture
def captured_logs():
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


def events(stream, event_type="security_event"):
    return [event for line in stream.getvalue().splitlines()
            if (event := json.loads(line))["event"] == event_type]


@pytest.fixture
def auth_client(monkeypatch):
    repository = Mock()
    repository.get_by_username.side_effect = lambda username: (
        SimpleNamespace(username=username, password_hash="private-hash")
        if username == "private-admin" else None
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda password, _: password == "private-correct-password",
    )
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix="/api")
    app.add_middleware(RequestLoggingMiddleware, trusted_proxy_cidrs=("10.0.1.0/24",))
    app.dependency_overrides[get_auth_service] = lambda: AuthService(repository)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, repository


@pytest.mark.parametrize("username,password,status,outcome,reason", [
    ("private-admin", "private-correct-password", 200, "success", None),
    ("private-admin", "private-wrong-password", 401, "rejected", "invalid_credentials"),
    ("private-unknown-admin", "private-wrong-password", 401, "rejected", "invalid_credentials"),
])
def test_login_outcomes_and_request_correlation(
    auth_client, captured_logs, username, password, status, outcome, reason,
):
    client, _ = auth_client
    response = client.post("/api/auth/login", json={
        "username": username, "password": password,
    })
    security_events = events(captured_logs)
    assert response.status_code == status
    assert len(security_events) == 1
    event = security_events[0]
    assert event["action"] == "admin_login"
    assert event["outcome"] == outcome
    assert event.get("reason") == reason
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert event["request_id"] == events(captured_logs, "http_request")[0]["request_id"]
    output = captured_logs.getvalue()
    for secret in (username, password, "private-hash"):
        assert secret not in output
    if status == 200:
        assert response.json()["access_token"] not in output


def test_malformed_login_is_logged_without_submitted_values(auth_client, captured_logs):
    client, _ = auth_client
    response = client.post("/api/auth/login", json={"username": "private-submitted-name"})
    event = events(captured_logs)[0]
    assert response.status_code == 422
    assert event["action"] == "admin_login"
    assert event["reason"] == "invalid_request"
    assert "private-submitted-name" not in captured_logs.getvalue()


def test_authentication_error_is_not_a_bad_password(auth_client, captured_logs):
    client, repository = auth_client
    repository.get_by_username.side_effect = RuntimeError("private-database-error")
    response = client.post("/api/auth/login", json={"username": "x", "password": "y"})
    event = events(captured_logs)[0]
    assert response.status_code == 500
    assert event["outcome"] == "error"
    assert event["level"] == "ERROR"
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert "private-database-error" not in captured_logs.getvalue()


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer private-invalid-token"}])
def test_denied_access_is_logged(auth_client, captured_logs, headers):
    client, _ = auth_client
    response = client.get("/api/auth/test", headers=headers)
    event = events(captured_logs)[0]
    assert response.status_code in (401, 403)
    assert event["action"] == "access_denied"
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert "private-invalid-token" not in captured_logs.getvalue()


@pytest.mark.parametrize("path,method", [("/api/auth/login", "POST"), ("/api/auth/test", "GET")])
@pytest.mark.parametrize("peer,expected,source", [
    ("10.0.1.5", "203.0.113.9", "alb"),
    ("198.51.100.8", "198.51.100.8", "peer"),
])
def test_security_events_include_resolved_ip_only(
    auth_client, captured_logs, path, method, peer, expected, source,
):
    existing_client, _ = auth_client
    with TestClient(existing_client.app, client=(peer, 50000)) as client:
        response = client.request(method, path, headers={
            "X-Forwarded-For": "192.0.2.123, 203.0.113.9",
        }, **({"json": {"username": "x", "password": "y"}} if method == "POST" else {}))
    event = events(captured_logs)[0]
    assert event["client_ip"] == expected
    assert event["client_ip_source"] == source
    assert event["request_id"] == response.headers["X-Request-ID"]
    assert "client_ip" not in events(captured_logs, "http_request")[0]
    assert "192.0.2.123" not in captured_logs.getvalue()


@pytest.mark.parametrize("password,status", [
    ("private-correct-password", 200), ("private-wrong-password", 401),
])
def test_cloudflare_visitor_is_recorded_for_login(auth_client, captured_logs, password, status):
    existing_client, _ = auth_client
    with TestClient(existing_client.app, client=("10.0.1.5", 50000)) as client:
        response = client.post("/api/auth/login", json={
            "username": "private-admin", "password": password,
        }, headers={
            "X-Forwarded-For": "192.0.2.123, 172.70.80.213",
            "CF-Connecting-IP": "198.51.100.25",
        })
    event = events(captured_logs)[0]
    assert response.status_code == status
    assert event["client_ip"] == "198.51.100.25"
    assert event["client_ip_source"] == "cloudflare"
    assert event["request_id"] == response.headers["X-Request-ID"]
    for excluded in ("192.0.2.123", "172.70.80.213", password):
        assert excluded not in captured_logs.getvalue()


@pytest.mark.parametrize("result", ["success", "missing", "commit_failure"])
def test_password_reset_outcomes(monkeypatch, captured_logs, result):
    db = Mock()
    admin = SimpleNamespace(password_hash="old-hash")
    db.query.return_value.filter.return_value.first.return_value = (
        None if result == "missing" else admin
    )
    monkeypatch.setattr(reset_script, "SessionLocal", lambda: db)
    monkeypatch.setattr(reset_script, "hash_password", lambda _: "private-new-hash")
    if result == "commit_failure":
        db.commit.side_effect = RuntimeError("private-reset-error")
        with pytest.raises(RuntimeError):
            reset_script.reset_admin_password()
        db.rollback.assert_called_once()
    else:
        reset_script.reset_admin_password()
    recorded = events(captured_logs)
    assert len(recorded) == 2
    assert recorded[0]["outcome"] == "started"
    assert recorded[1]["outcome"] == {
        "success": "success", "missing": "rejected", "commit_failure": "error",
    }[result]
    assert recorded[0]["operation_id"] == recorded[1]["operation_id"]
    assert all("client_ip" not in event for event in recorded)
    if result == "success":
        db.commit.assert_called_once()
    elif result == "missing":
        db.commit.assert_not_called()
    db.close.assert_called_once()
    for secret in ("private-new-hash", "private-reset-error", reset_script.settings.admin_password):
        assert secret not in captured_logs.getvalue()
