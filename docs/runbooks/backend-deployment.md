# Backend deployment and rollback

## Purpose

Deploy a backend image from Amazon ECR to the portfolio EC2 instance.

GitHub Actions tests the backend, builds the image, checks container health,
and publishes it to ECR after successful pushes to main.
Deployment to EC2 is currently manual.

Replacing the container briefly interrupts backend traffic.

## Prerequisites

- AWS region: us-east-2
- EC2 instance: i-068ba6708472b588f
- Connect through AWS Systems Manager Session Manager.
- The EC2 role must allow ECR image downloads.
- Production configuration must exist at /opt/portfolio/backend.env.
- Keep this file owned by root with permissions 600.
- Never paste configuration values into GitHub, terminal output, or this runbook.
- Record the current image digest and the new published image digest.
- Review database changes before deploying. Restoring a container does not undo
  database migrations.

## 1. Check the current backend

```bash
sudo docker ps -a --filter name=portfolio-backend \
  --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

sudo docker inspect portfolio-backend \
  --format 'Image: {{.Config.Image}} | Restart: {{.HostConfig.RestartPolicy.Name}}'

curl --fail --silent --show-error \
  --write-out '\nHTTP %{http_code}\n' \
  http://127.0.0.1:8000/health
```

Expect the current backend to be healthy and return HTTP 200 with
{"status":"ok"}.

Before continuing, resolve any existing containers named
portfolio-backend-candidate or portfolio-backend-rollback.
Do not overwrite or delete a rollback container without reviewing whether
it is still needed.

## 2. Authenticate and pull the new image

Replace REPLACE_WITH_NEW_DIGEST with the published image's SHA-256 digest.
Use the full digest, not a shortened value.

```bash
NEW_IMAGE='327425719636.dkr.ecr.us-east-2.amazonaws.com/portfolio-backend@sha256:REPLACE_WITH_NEW_DIGEST'

aws ecr get-login-password --region us-east-2 \
  | sudo docker login --username AWS --password-stdin \
    327425719636.dkr.ecr.us-east-2.amazonaws.com

sudo docker pull "$NEW_IMAGE"
```

Stop if authentication or the download fails.

## 3. Check a candidate container

The candidate uses production configuration and can access production services.
Limit checks to operations that do not change production data.

```bash
sudo docker run -d --name portfolio-backend-candidate \
  --env-file /opt/portfolio/backend.env \
  -p 127.0.0.1:8001:8000 \
  "$NEW_IMAGE"
```

Allow startup time, then check:

```bash
curl --fail --silent --show-error \
  --write-out '\nHTTP %{http_code}\n' \
  http://127.0.0.1:8001/health

sudo docker inspect portfolio-backend-candidate \
  --format 'State: {{.State.Status}} | Health: {{.State.Health.Status}}'
```

Proceed only when the response is HTTP 200 with {"status":"ok"}
and Docker reports running and healthy.

The health endpoint confirms the application responds; it does not verify
every feature or database operation.

## 4. Replace the serving backend

These commands match the current deployment: default bridge networking,
port 8000, no mounts, and configuration from backend.env.
Review the commands if those settings change.

```bash
sudo docker stop portfolio-backend &&
sudo docker rename portfolio-backend portfolio-backend-rollback &&
sudo docker run -d --name portfolio-backend \
  --restart unless-stopped \
  --env-file /opt/portfolio/backend.env \
  -p 8000:8000 \
  "$NEW_IMAGE"
```

If a command fails, inspect the container state before continuing.

## 5. Verify the deployment

```bash
curl --fail --silent --show-error \
  --write-out '\nHTTP %{http_code}\n' \
  http://127.0.0.1:8000/health

sudo docker inspect portfolio-backend \
  --format 'Image: {{.Config.Image}} | State: {{.State.Status}} | Health: {{.State.Health.Status}}'
```

Expect the selected image, HTTP 200, and Docker health healthy.
Docker may initially report health: starting.

In AWS:

1. Open EC2 → Target Groups → portfolio-backend-tg → Targets.
2. Confirm i-068ba6708472b588f on port 8000 is Healthy.

Open https://www.ericrobinsonjr.com and check the home page,
project details, images, and relevant backend features.

## 6. Roll back if verification fails

Run these only when the replacement container is named portfolio-backend
and the previous container is named portfolio-backend-rollback.

```bash
sudo docker stop portfolio-backend &&
sudo docker rm portfolio-backend &&
sudo docker rename portfolio-backend-rollback portfolio-backend &&
sudo docker start portfolio-backend
```

If creation of the replacement failed and no portfolio-backend container
exists, rename and start the rollback container directly.

Repeat local health, Docker health, load balancer, and website checks.

## 7. Clean up after successful verification

```bash
sudo docker stop portfolio-backend-candidate &&
sudo docker rm portfolio-backend-candidate

sudo docker logout 327425719636.dkr.ecr.us-east-2.amazonaws.com
```

Keep portfolio-backend-rollback stopped during the agreed rollback period.
Retain its image in ECR and on the instance.

## Deployment record

For each deployment, record:

- Date and operator
- Commit and GitHub Actions run
- Previous and new image digests
- Health and website verification results
- Whether rollback was performed

During the initial deployment exercise, the new backend passed local health,
Docker health, load balancer health, and manual website checks.
Rollback to the previous version was rehearsed successfully before redeploying.