# HTTP request logging

## Purpose and flow

Use request logs to investigate failed endpoints, slow backend requests, and
which response belongs to a reported request. Security events explain login
outcomes; traces explain time spent inside an operation.

```text
FastAPI request logging middleware
  -> one JSON http_request event on stdout
  -> Docker awslogs driver
  -> CloudWatch Logs /portfolio/production/backend in us-east-2
```

The middleware is in `app/core/logging.py`. It wraps downstream HTTP handling,
adds an `X-Request-ID` response header, and writes the event when handling exits.
It also logs requests that raise exceptions. WebSocket and lifespan scopes pass
through without an HTTP request event.

The application generates logs while running on EC2. ECR stores the container
image; it does not run the application or generate request logs. The deployment
script configures delivery, and `infra/cloudwatch.yaml` manages the log group
and the EC2 role's log-writing policy.

## Fields and interpretation

| Field | Meaning |
| --- | --- |
| `timestamp` | Application timestamp in UTC. |
| `level` | ERROR for a recorded status of 500 or higher; otherwise INFO. |
| `service` | `portfolio-backend`. |
| `event` | `http_request`, distinguishing this record from security events. |
| `request_id` | Application-generated UUID matching the response's `X-Request-ID`. |
| `method` | HTTP method, such as GET or POST. |
| `route` | Route pattern, such as `/api/projects/{project_id}`, or `<unmatched>`. |
| `status_code` | Captured response status; initialized to 500 for failures before a response starts. |
| `duration_ms` | Time through downstream backend handling, rounded to two decimal places. |
| `error_type` | Exception class when an exception escapes downstream handling; no exception message. |
| `trace_id`, `span_id` | Present when a valid current trace span exists. See the tracing runbook. |

A 401 login response can be an expected rejection. A 500 indicates an internal
failure. A long duration is a performance symptom; it alone does not prove a
database error. The timer includes work and waiting inside the backend, but
does not measure the full browser-to-Cloudflare-to-ALB journey.

These JSON events exclude bodies, headers, query strings, credentials, tokens,
exception messages, and IP addresses. Route parameters are represented by the
route pattern rather than their submitted values. Other container output, such
as server startup messages or tracebacks, is separate from this custom JSON
format and may have different contents.

## Log groups and streams

Open CloudWatch Logs in **us-east-2** and select
`/portfolio/production/backend`. Choose a time range covering the incident.
Search across the log group when requests might span multiple deployments.

The deployment script does not set `awslogs-stream`, so Docker names each
stream after the container ID. A normal deployment creates a candidate container
and then a serving container, which explains two new streams. Restarting the
same container keeps its ID; replacing it creates another stream. Old streams
can remain after their containers stop. See the
[Docker awslogs stream documentation](https://docs.docker.com/engine/logging/drivers/awslogs/#awslogs-stream).

To identify the current container and its configured log driver, run these
read-only commands in the EC2 Systems Manager shell:

```sh
sudo docker inspect --format '{{.Id}}' portfolio-backend
sudo docker inspect --format '{{json .HostConfig.LogConfig}}' portfolio-backend
```

Keep application timestamps in UTC for correlation. Select a convenient console
display time zone and account for that offset when comparing an email or screenshot.

## Useful CloudWatch log-event filters

These are CloudWatch JSON filter patterns, not SQL or Logs Insights queries.
Enter them in the log-event filter bar and apply the filter.

All HTTP requests:

```text
{ $.event = "http_request" }
```

Requests excluding health checks:

```text
{ $.event = "http_request" && $.route != "/health" }
```

Server errors:

```text
{ $.event = "http_request" && $.status_code >= 500 }
```

Requests taking at least one second:

```text
{ $.event = "http_request" && $.duration_ms >= 1000 }
```

Follow one request across HTTP and security events, replacing the placeholder:

```text
{ $.request_id = "REQUEST_ID_FROM_RESPONSE_OR_LOG" }
```

Health checks are real requests. Docker checks `/health` every 30 seconds with
the current Dockerfile; the ALB and deployment script also probe it. Excluding
them in a view hides them from that view without stopping their collection.
Excluding health checks does not prove remaining requests came from people;
bots and other automated clients can call the same routes.

## Investigation and missing logs

1. Record the incident time, endpoint, and response request ID if available.
2. Search the log group over that time range, including earlier container streams.
3. Check status, duration, and any exception class. For login requests, match
   the request ID to the security event for its outcome and reason.
4. If tracing is active, use the trace ID to compare authentication and lookup
   durations. Do not put passwords or tokens into searches.
5. For absent events, verify the backend is running, the region and time range
   are correct, and the latest serving stream is selected. Clear restrictive
   filters to look for startup output.
6. Check the container's log driver, EC2 role permissions for
   `logs:CreateLogStream` and `logs:PutLogEvents`, and the Docker daemon's delivery
   errors. Do not broaden IAM permissions as a troubleshooting shortcut.

The template sets seven-day retention and retains the log group on stack
deletion/replacement. Retaining the group does not preserve events beyond its
retention policy.

## Changes, verification, and costs

Update application logging through the normal code review and deployment flow.
Update log-group configuration through a reviewed CloudFormation change set.
A Git push alone does not apply the template to the stack.

Local checks in the active `.venv312` terminal:

```powershell
python -m pytest tests/test_request_logging.py tests/test_security_logging.py -v
git diff --check
```

After an authorized deployment, make a normal request and confirm its response
request ID matches the new HTTP event. The EC2 backend must be running for this
live check; local tests do not need it.

Writing this guide creates no AWS resources. Existing log ingestion and storage
can incur charges, and starting EC2 or running live tests can add usage. Review
[CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/) before increasing
log volume or retention. Account credits and free allowances are not assumed.

## Related guides

- [Admin security logging](admin-security-logging.md)
- [Admin login metrics and alerts](admin-login-monitoring.md)
- [Request tracing](request-tracing.md)
- [Backend deployment](backend-deployment.md)
