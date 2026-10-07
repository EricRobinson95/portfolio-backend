#!/usr/bin/env bash
set -Eeuo pipefail

# Run before backend cutover. IAM permissions are deployed through CloudFormation.
IMAGE="public.ecr.aws/aws-observability/aws-otel-collector:v0.50.0"
NAME="portfolio-otel"
CONFIG_SOURCE="${1:?Provide the repository collector configuration path}"
CONFIG_TARGET="/opt/portfolio/otel-collector.yaml"

[[ "$EUID" -eq 0 ]] || { echo "Run as root."; exit 1; }
test -f "$CONFIG_SOURCE"
for tool in docker curl sha256sum; do command -v "$tool" >/dev/null; done

exec 8>/run/portfolio-trace-collector.lock
flock -n 8 || { echo "Another collector installation is running."; exit 1; }

BIND_IP="$(docker network inspect bridge --format '{{(index .IPAM.Config 0).Gateway}}')"
[[ "$BIND_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
  echo "Could not determine Docker's IPv4 bridge gateway."; exit 1;
}
CONFIG_SHA="$(sha256sum "$CONFIG_SOURCE" | cut -d ' ' -f 1)"

if docker container inspect "$NAME" >/dev/null 2>&1; then
  # Do not replace an existing collector silently during application deployment.
  actual="$(docker inspect --format '{{index .Config.Labels "portfolio.collector.config-sha"}}|{{index .Config.Labels "portfolio.collector.image"}}|{{index .Config.Labels "portfolio.collector.bind-ip"}}' "$NAME")"
  [[ "$actual" == "${CONFIG_SHA}|${IMAGE}|${BIND_IP}" ]] || {
    echo "Existing collector differs from this release; review its upgrade separately."; exit 1;
  }
  [[ "$(docker inspect --format '{{.State.Running}}' "$NAME")" == "true" ]] || docker start "$NAME" >/dev/null
else
  install -d -m 755 /opt/portfolio
  install -m 600 -o root -g root "$CONFIG_SOURCE" "$CONFIG_TARGET"
  docker pull "$IMAGE"
  # Run the exact digest pulled, so a container restart does not select another image.
  DIGEST="$(docker image inspect --format '{{index .RepoDigests 0}}' "$IMAGE")"
  docker run -d --name "$NAME" \
    --restart unless-stopped \
    --network host \
    --user 0:0 \
    --read-only \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --memory 256m --memory-swap 256m --cpus 0.25 \
    --log-driver json-file \
    --log-opt max-size=10m --log-opt max-file=3 \
    --label "portfolio.collector.config-sha=${CONFIG_SHA}" \
    --label "portfolio.collector.image=${IMAGE}" \
    --label "portfolio.collector.bind-ip=${BIND_IP}" \
    -e "OTEL_BIND_IP=${BIND_IP}" \
    -e AWS_REGION=us-east-2 \
    -v "${CONFIG_TARGET}:/etc/otel-collector.yaml:ro" \
    "$DIGEST" --config=/etc/otel-collector.yaml
fi

for attempt in {1..30}; do
  if curl --fail --silent --max-time 2 http://127.0.0.1:13133/ >/dev/null; then
    echo "Collector is ready; verify trace delivery after backend deployment."
    exit 0
  fi
  [[ "$(docker inspect --format '{{.State.Running}}' "$NAME")" == "true" ]] || break
  sleep 1
done
echo "Collector failed its readiness check; serving backend remains unchanged."
docker logs --tail 30 "$NAME"
exit 1
