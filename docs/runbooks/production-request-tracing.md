# Production request tracing with OpenTelemetry and AWS X-Ray

## What each component does

```text
Visitor -> Cloudflare -> ALB -> FastAPI on EC2
                              | creates spans
                              v
                    SDK background batch processor
                              | OTLP/HTTP, Docker bridge only
                              v
                     ADOT collector on the same EC2
                              | authenticated with EC2 IAM role
                              v
                         AWS X-Ray, us-east-2
```

OpenTelemetry creates timing records. Its OTLP exporter transports them to a
collector. The collector converts them to X-Ray segments and uploads them.
X-Ray provides the stored trace and timeline. Existing request logs, security
logs, metrics, alarms, and dashboards remain operational independently.

Only backend handling is traced. Browser, Cloudflare, and ALB time are outside
these spans. `admin.lookup` includes the whole repository call rather than just
SQL execution on the database server. Credentials, tokens, IP addresses, actual
URL values, SQL parameters, and exception messages are not attached to spans.
Do not add automatic HTTP or SQL instrumentation without reviewing its fields.

## Changes in the repository

- `app/core/tracing.py`: OTLP exporter, bounded background queue (2048 spans),
  batches up to 128 spans, 1 second scheduling delay, 3 second exporter timeout,
  AWS-compatible trace IDs, and parent-aware sampling.
- `app/core/logging.py`: fixed endpoint classification for the sampling decision;
  no raw path is exported. Logs gain `xray_trace_id` and `trace_sampled`.
- `infra/otel-collector.yaml`: OTLP receiver, memory limiter, batching, and X-Ray
  exporter. Only request ID, operation, and outcome are indexed as annotations.
- `infra/cloudwatch.yaml`: adds `BackendTraceWriterPolicy` to the existing
  `portfolio-ec2-role`. It grants `xray:PutTraceSegments` and
  `xray:PutTelemetryRecords`. These actions require `Resource: "*"`; this does
  not grant read access or administration of other AWS services.
- `scripts/install-trace-collector.sh`: installs the pinned ADOT v0.50.0 image,
  resolves the pulled image to a digest, and verifies collector readiness.
- Deployment workflow: transfers the collector configuration and installer
  through the existing SSM command and runs them before backend cutover.
- Backend deployment: enables OTLP tracing and resolves the collector hostname
  through Docker's host gateway. A configured `TRACING_ENABLED=false` is honored.

The collector uses host networking to obtain IMDS instance-role credentials
without changing the EC2 metadata hop limit. Its OTLP receiver binds only to
Docker's bridge gateway. Its health endpoint binds only to loopback. Do not open
ports 4318 or 13133 in security groups or expose them through the ALB. This is a
trusted single-host setup; other local Docker containers can reach the receiver.
Only run trusted containers on this host. No access keys or Docker socket are
mounted into the collector.

The collector is capped at 256 MiB RAM and 0.25 CPU. Its limiter starts rejecting
telemetry under memory pressure; its local diagnostic logs rotate at 10 MiB with
three files. These limits reduce resource contention but do not guarantee that
a t3.micro has sufficient spare capacity. Check memory and CPU during rollout.
Application telemetry is best effort: queue overflow, network/export failures,
forced container termination, or collector restart can lose spans. A collector
readiness check does not prove AWS permissions or successful trace delivery.
SDK shutdown attempts to flush; the deployment allows 30 seconds for stopping
the backend. Login security logs and their metric remain the audit/alert path.

## Sampling and costs

- Health endpoint: no stored traces. Its HTTP logs still exist.
- Admin login endpoint: every request is selected, including rejected attempts.
- Other HTTP endpoints: approximately 10%, configurable through
  `TRACING_SAMPLE_RATIO` in the backend environment file (0 through 1).
- Children inherit the parent decision, preserving a coherent timeline.

This is SDK sampling, not an X-Ray centralized sampling rule. A selected trace
can still be lost during export. An unsampled ordinary failure will still have
request logs but no stored trace. Trace IDs in unsampled logs are not proof of
delivery; check `trace_sampled` and the X-Ray view.

Pricing checked on October 6, 2026: AWS lists the first 100,000 recorded traces
and first 1,000,000 retrieved/scanned traces per month as free. After those
account-wide allowances, the published rates are $5 per million recorded and
$0.50 per million retrieved/scanned. Other services can consume the allowances.
For example, 200,000 recorded traces total would have a $0.50 recording charge
if the full 100,000 allowance remains available. This is not a spending cap.
An attack against login can increase trace volume because login is fully sampled.
[AWS pricing](https://aws.amazon.com/cloudwatch/pricing/)

No new EC2 instance, NAT gateway, log group, or Application Signals service is
created. Existing EC2, ALB, database, storage, and log charges continue. The
collector consumes resources on EC2 and uses network egress. X-Ray's retention
is separate from the log group's seven-day retention. This change does not
enable X-Ray Insights or Application Signals.

## Rollout order

1. Review and test the branch locally. Install updated dependencies into
   `.venv312` with `python -m pip install -r requirements-dev.txt`, then run
   `python -m pytest -v` and `git diff --check`. Confirm CI also passes.
2. Update the existing `portfolio-backend-observability` CloudFormation stack
   with `infra/cloudwatch.yaml`. Use change set name
   `add-backend-xray-trace-permissions`. Preserve the role and email parameters.
   Expected change: add `BackendTraceWriterPolicy`, without replacing existing
   log, metric, alarm, SNS, or dashboard resources. Review and execute the change
   set; wait for `UPDATE_COMPLETE` before merging the code.
3. Ensure EC2 is running and online in Systems Manager. The current deployment
   must be healthy. This host must be able to pull the public ADOT image and
   reach X-Ray over HTTPS; investigate egress before creating new paid networking.
4. Merge the reviewed PR. The main workflow installs/verifies the collector,
   then deploys the tested backend image with tracing enabled. The collector
   installer fails safely if a pre-existing collector has different image or
   configuration labels, requiring an explicit upgrade review.
5. Verify the workflow and serving backend health. Make one rejected login on
   your own admin page. Leave passwords and tokens out of notes or screenshots.
6. In CloudWatch Logs, filter `{ $.event = "security_event" &&
   $.action = "admin_login" }`, find the new request, and confirm
   `trace_sampled: true`. Copy its `xray_trace_id`.
7. In CloudWatch's trace view in `us-east-2`, search that X-Ray trace ID or the
   `portfolio-backend` service over the recent time window. Allow batching and
   AWS ingestion time. Open the trace and verify its HTTP and authentication
   spans. A rejected login should include lookup and, for a known admin,
   password verification. Successful login also includes token creation.
8. Confirm ordinary health checks have no stored spans and existing security
   metrics/alarms still behave as before. Do not generate extra alarm tests
   just to verify tracing.

Git merging deploys the application and collector; it does not apply the IAM
CloudFormation template. Uploading the template does not deploy application code.
Local tests and collector readiness do not certify live AWS delivery. Record
the merge/image digest and the first observed production trace after rollout.

## Read-only checks in the EC2 SSM session

```sh
sudo docker ps --filter name=portfolio-otel
sudo docker stats --no-stream portfolio-otel portfolio-backend
sudo docker logs --tail 50 portfolio-otel
curl --fail --silent http://127.0.0.1:13133/
sudo docker exec portfolio-backend python -c 'import os; print({key: os.getenv(key) for key in ("TRACING_ENABLED", "TRACING_EXPORTER", "TRACING_OTLP_ENDPOINT", "TRACING_SAMPLE_RATIO")})'
```

Print only these tracing settings, not the entire environment file. If export
fails with AccessDenied, verify the stack policy is attached to the actual EC2
role. For credential errors, verify the role and IMDS are available. For timeouts,
inspect the collector's logs and outbound connectivity. If the application cannot
reach the collector, verify its Docker bridge binding and backend hostname alias.
If the collector config changes, archive the stopped old collector and verify
the replacement separately rather than silently replacing it during deployment.

## Disable and recovery

Set `TRACING_ENABLED=false` in `/opt/portfolio/backend.env` while preserving
`600:root:root`, then redeploy the current approved backend image using the
deployment runbook. Editing the file alone does not change a running container.
Do not use `docker restart` to load changed environment variables; recreate
through the deployment procedure. Once tracing is disabled, the collector can
be stopped with `sudo docker stop portfolio-otel` to release its RAM. Starting
it again is required before re-enabling tracing. No database restore is involved.

If the new backend fails its health checks, the existing deployment rollback
restores the previous container. Collector readiness failure occurs before the
serving backend is replaced. Collector export failure after startup does not
trigger automatic backend rollback; investigate trace delivery separately.

## Sources and related procedures

- [OpenTelemetry exporters](https://opentelemetry.io/docs/languages/python/exporters/)
- [AWS OpenTelemetry manual instrumentation](https://aws-otel.github.io/docs/getting-started/python-sdk/manual-instr/)
- [ADOT downloads](https://aws-otel.github.io/download/)
- [X-Ray exporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/awsxrayexporter)
- [Request tracing](request-tracing.md)
- [Request logs](http-request-logging.md)
- [Admin security monitoring](admin-login-monitoring.md)
- [Backend deployment and rollback](backend-deployment.md)
