#!/usr/bin/env bash
set -Eeuo pipefail

REGISTRY="327425719636.dkr.ecr.us-east-2.amazonaws.com"
REPOSITORY="${REGISTRY}/portfolio-backend"
ENV_FILE="/opt/portfolio/backend.env"
CURRENT="portfolio-backend"
CANDIDATE="portfolio-backend-candidate"
ROLLBACK="portfolio-backend-rollback"
NEW_IMAGE="${1:-}"

# Accept only a digest from this backend repository.
if [[ ! "$NEW_IMAGE" =~ ^${REPOSITORY//./\\.}@sha256:[a-f0-9]{64}$ ]]; then
  echo "Provide the full backend ECR image URI with its SHA-256 digest."
  exit 1
fi

if [[ "$EUID" -ne 0 ]]; then
  echo "Run this script as root."
  exit 1
fi

# Prevent overlapping deployments on this instance.
exec 9>/run/portfolio-backend-deploy.lock
flock -n 9 || {
  echo "Another backend deployment is running."
  exit 1
}

for tool in docker aws curl python3; do
  command -v "$tool" >/dev/null
done

test -f "$ENV_FILE"
if [[ "$(stat -c '%a:%U:%G' "$ENV_FILE")" != "600:root:root" ]]; then
  echo "backend.env must be owned by root:root with permissions 600."
  exit 1
fi

# Production is enabled by default once the collector is installed. An operator
# can disable export explicitly without changing or printing other env values.
TRACING_ENABLED="$(python3 - "$ENV_FILE" <<'PY'
import pathlib
import sys

value = "true"
for line in pathlib.Path(sys.argv[1]).read_text().splitlines():
    key, separator, candidate = line.partition("=")
    if separator and key.strip() == "TRACING_ENABLED":
        value = candidate.strip().strip("\"'").lower()
if value not in {"true", "false"}:
    raise SystemExit("TRACING_ENABLED must be true or false when configured.")
print(value)
PY
)"
if [[ "$TRACING_ENABLED" == "true" ]]; then
  [[ "$(docker inspect --format '{{.State.Running}}' portfolio-otel 2>/dev/null)" == "true" ]] &&
    curl --fail --silent --max-time 3 http://127.0.0.1:13133/ >/dev/null || {
      echo "Trace collector is unavailable; serving backend remains unchanged."
      exit 1
    }
fi

exists() {
  docker container inspect "$1" >/dev/null 2>&1
}

wait_healthy() {
  local name="$1" port="$2"
  local deadline=$((SECONDS + 120))

  while (( SECONDS < deadline )); do
    if [[ "$(docker inspect --format '{{.State.Status}}' "$name")" != "running" ]]; then
      return 1
    fi

    if [[ "$(docker inspect --format '{{.State.Health.Status}}' "$name")" == "healthy" ]] &&
      curl --fail --silent --max-time 3 \
        "http://127.0.0.1:${port}/health" |
        python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin) == {"status": "ok"} else 1)'
    then
      return 0
    fi
    sleep 3
  done
  return 1
}

exists "$CURRENT" || {
  echo "No existing backend container found."
  exit 1
}

if exists "$CANDIDATE"; then
  echo "An existing candidate container needs review before deployment."
  exit 1
fi

wait_healthy "$CURRENT" 8000 || {
  echo "Current backend is unhealthy; investigate before deploying."
  exit 1
}

if exists "$ROLLBACK"; then
  if [[ "$(docker inspect --format '{{.State.Running}}' "$ROLLBACK")" != "false" ]]; then
    echo "Rollback container is running; investigate before deploying."
    exit 1
  fi
fi

candidate_owned=0
cutover_started=0
old_renamed=0
export DOCKER_CONFIG
DOCKER_CONFIG="$(mktemp -d)"

finish() {
  local result=$?
  trap - EXIT
  set +e

  if (( result != 0 && cutover_started == 1 )); then
    echo "Deployment failed; restoring the previous backend."

    if (( old_renamed == 1 )); then
      if exists "$CURRENT"; then
        docker rm -f "$CURRENT" >/dev/null
      fi
      docker rename "$ROLLBACK" "$CURRENT"
    fi

    docker start "$CURRENT" >/dev/null
    if wait_healthy "$CURRENT" 8000; then
      echo "Previous backend restored and healthy."
    else
      echo "ROLLBACK NEEDS ATTENTION: previous backend failed verification."
    fi
  fi

  if (( candidate_owned == 1 )); then
    docker rm -f "$CANDIDATE" >/dev/null 2>&1
  fi

  rm -rf -- "$DOCKER_CONFIG"
  exit "$result"
}
trap finish EXIT

aws ecr get-login-password --region us-east-2 |
  docker login --username AWS --password-stdin "$REGISTRY"

docker pull "$NEW_IMAGE"

candidate_owned=1
docker run -d --name "$CANDIDATE" \
  --add-host portfolio-otel:host-gateway \
  -e "TRACING_ENABLED=${TRACING_ENABLED}" \
  -e TRACING_EXPORTER=otlp \
  -e TRACING_OTLP_ENDPOINT=http://portfolio-otel:4318/v1/traces \
  --log-driver awslogs \
  --log-opt awslogs-region=us-east-2 \
  --log-opt awslogs-group=/portfolio/production/backend \
  --env-file "$ENV_FILE" \
  -p 127.0.0.1:8001:8000 \
  "$NEW_IMAGE"

wait_healthy "$CANDIDATE" 8001 || {
  echo "Candidate failed health checks; serving backend remains in place."
  exit 1
}

# Preserve earlier rollback containers instead of deleting them.
if exists "$ROLLBACK"; then
  archive="${ROLLBACK}-$(date -u +%Y%m%dT%H%M%SZ)-$$"
  docker rename "$ROLLBACK" "$archive"
  echo "Earlier rollback container preserved as ${archive}."
fi

cutover_started=1
docker stop --time 30 "$CURRENT"
docker rename "$CURRENT" "$ROLLBACK"
old_renamed=1

docker run -d --name "$CURRENT" \
  --add-host portfolio-otel:host-gateway \
  -e "TRACING_ENABLED=${TRACING_ENABLED}" \
  -e TRACING_EXPORTER=otlp \
  -e TRACING_OTLP_ENDPOINT=http://portfolio-otel:4318/v1/traces \
  --restart unless-stopped \
  --log-driver awslogs \
  --log-opt awslogs-region=us-east-2 \
  --log-opt awslogs-group=/portfolio/production/backend \
  --env-file "$ENV_FILE" \
  -p 8000:8000 \
  "$NEW_IMAGE"

wait_healthy "$CURRENT" 8000 || {
  echo "Replacement backend failed health checks."
  exit 1
}

echo "Backend deployed and healthy: ${NEW_IMAGE}"
echo "Previous backend retained as ${ROLLBACK}."
