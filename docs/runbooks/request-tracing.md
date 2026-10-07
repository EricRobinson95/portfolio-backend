# Local request tracing

## What a trace measures

The request logging middleware starts a server span for each HTTP request. It
keeps that span current while the downstream application handles the request and
while request and security logs are written. Authentication creates child spans:

```text
POST /api/auth/login
└── admin.authenticate
    ├── admin.lookup
    ├── admin.verify_password
    └── admin.create_token
```

An unknown admin stops after lookup. A wrong password stops after verification.
A database exception marks lookup, authentication, and the HTTP span as errors.
A 401 rejection leaves span status UNSET and records the login outcome as rejected.
HTTP responses of 500 or higher mark the server span ERROR, including handled
exceptions that become responses without escaping the router.

The HTTP span covers downstream backend handling from this middleware, including
waiting for dependencies, authentication, serialization, and response sending.
It does not measure browser, Cloudflare, or ALB latency. An unhandled exception's
outer FastAPI error response can be sent after the span has ended. The lookup
span measures the repository call, not database server execution time alone.
Child durations are already included in the parent duration; do not add them
to the parent to calculate total time. Local synchronous console exporting adds
some overhead to enclosing spans.

## Correlating logs

- `request_id`: identifies the request and appears in `X-Request-ID` responses.
- `trace_id`: identifies the trace containing the HTTP and authentication spans.
- `span_id`: identifies the span current when a log is written.

Request and middleware security logs have the HTTP span's IDs. The HTTP span
also includes `app.request_id`, connecting a browser response ID to the trace.
When no valid current span exists, logs omit trace and span IDs.

This lesson creates backend traces and does not extract incoming `traceparent`
headers. Browser, Cloudflare, and ALB tracing are not connected to this trace.
Spans use route patterns, such as `/items/{item_id}`, rather than actual paths.
Unmatched requests use a method-only span name. Spans exclude request bodies,
query strings, headers, usernames, passwords, hashes, tokens, and exception text.
They include safe exception class names when an operation fails.

## Local configuration and checks

Tracing defaults to disabled. Enable it only in the local development process
when ready to inspect console spans. The example environment file documents
`TRACING_ENABLED=false`; it does not change the active environment.

From the repository root with `.venv312` active:

```powershell
python -m pytest tests/test_tracing.py -v
python -m pytest -v
git diff --check
```

Tests use an in-memory exporter, fake repositories, and FastAPI's TestClient.
They do not call the production database or AWS. Test configuration disables
console tracing; tracing tests supply their own provider through monkeypatch.

The current production setup must keep tracing disabled. This exporter prints
to stdout and does not send traces to an AWS tracing service. Enabling it inside
the existing production Docker container would add span JSON to CloudWatch logs
through the existing Docker log driver, increasing log volume and potentially
cost. A production exporter, sampling, and cost review are separate work.
