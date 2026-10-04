# Runbook: backend container fails to start

## Scope
Local Docker troubleshooting using PowerShell and test configuration.
Container: portfolio-backend-debug
Image: portfolio-backend:ci

The /health endpoint verifies that the API responds. It does not
verify database connectivity or other application features.

## Symptoms
- The container exits shortly after creation.
- The health endpoint is unavailable.
- Docker reports Exited (1).

## Diagnose
Run:

```powershell
docker ps -a --filter "name=portfolio-backend-debug"
docker logs portfolio-backend-debug --tail 50
docker inspect --format '{{.State.Status}} exit={{.State.ExitCode}}' portfolio-backend-debug
```

For the missing-secret configuration failure, the logs show:

```text
ValidationError: 1 validation error for Settings
secret_key
  Field required
```

This means SECRET_KEY was missing when the app loaded its settings.
Exit code 1 alone does not identify the cause; check the logs.

## Recover
For this local test container, remove the stopped container:

```powershell
docker rm portfolio-backend-debug
```

Recreate it with all required test settings:

```powershell
docker run -d --name portfolio-backend-debug `
  -p 127.0.0.1:8001:8000 `
  -e DATABASE_URL=sqlite+pysqlite:///:memory: `
  -e SECRET_KEY=test-only-secret-key-at-least-32-bytes-long `
  -e PROJECT_NAME=PortfolioSmokeTest `
  -e API_VERSION=test `
  -e ADMIN_USERNAME=test-admin `
  -e ADMIN_PASSWORD=test-only-password `
  -e ENVIRONMENT=test `
  -e SERVE_LOCAL_STATIC_FILES=false `
  portfolio-backend:ci
```

These values are for local testing only.
Restarting the original container reuses its existing configuration;
recreation applies the corrected settings.

## Verify
Allow a few seconds for startup, then run:

```powershell
docker ps --filter "name=portfolio-backend-debug"
Invoke-RestMethod http://127.0.0.1:8001/health
docker logs portfolio-backend-debug --tail 20
```

Recovery evidence:
- Container remains Up and its Docker health check becomes healthy.
- The health request returns status: ok.
- Logs show Application startup complete and GET /health returning 200.

## If recovery fails
Read the new startup logs before choosing another fix.
If the error differs, this missing-SECRET_KEY procedure may not apply.
When asking for help, include the image tag, container state, and
relevant error lines. Remove credentials and sensitive data from logs.

## Cleanup
After completing the local exercise:

```powershell
docker stop portfolio-backend-debug
docker rm portfolio-backend-debug
```

## Validation record
2026-10-04: Reproduced startup failure by omitting SECRET_KEY.
Observed exit code 1 and a Settings validation error.
Recreated the container with the test setting and verified healthy
status, successful startup, and an HTTP 200 health response.