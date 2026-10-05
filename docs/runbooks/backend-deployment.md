# Backend deployment and rollback

## Purpose

Deploy validated backend images from Amazon ECR to the portfolio EC2 instance
through GitHub Actions and AWS Systems Manager.

After a successful push to main, the workflow tests the backend, builds and
checks the container, publishes the image to ECR, and deploys it by digest.

Replacing the serving container briefly interrupts backend traffic.

## Prerequisites

- AWS account: 327425719636
- AWS region: us-east-2
- EC2 instance: i-068ba6708472b588f
- EC2 must be running and available through Systems Manager before merging.
- Docker and the existing backend must be running and healthy.
- The instance requires aws, docker, curl, python3, and flock.
- The EC2 role must allow ECR image downloads and Systems Manager access.
- The GitHub role must allow ECR publishing, SSM SendCommand for this instance,
  and GetCommandInvocation.
- GitHub repository variables must include AWS_ROLE_ARN, AWS_REGION,
  and ECR_REPOSITORY.
- Production configuration must exist at /opt/portfolio/backend.env,
  owned by root:root with permissions 600.
- Never commit or share production configuration values.
- Review database changes before deploying. Container rollback does not undo
  database migrations.

## 1. Prepare and merge

1. Start EC2 if it is stopped.
2. Confirm it is available through Systems Manager Session Manager.
3. Confirm the existing backend is healthy.
4. Open the pull request and wait for required tests and Docker checks to pass.
5. Review the changes and merge into main.

Deployment is skipped for pull requests and pushes to feature branches.

Every push to main currently triggers publishing and deployment, including
documentation changes.

## 2. Monitor GitHub Actions

Open the repository's Actions page and select the run for the merged commit.

Expect these jobs to succeed:

1. Backend tests
2. Backend Docker build
3. Deploy backend to EC2

The Docker build summary records the published image URI with its digest.

The deployment summary records:

- Deployed image URI
- EC2 instance ID
- SSM command ID
- Container and local HTTP health check results

A successful deployment job confirms the automated checks passed.
Load balancer and website checks remain manual.

## 3. What the deployment script does

The workflow sends scripts/deploy-backend.sh through the SSM
AWS-RunShellScript document and runs it as root.

The script:

1. Validates the image digest and configuration file permissions.
2. Acquires a lock to prevent overlapping deployments on the instance.
3. Checks the existing backend's Docker and local HTTP health.
4. Stops if a candidate container already exists or the rollback container
   is running.
5. Authenticates to ECR using a temporary Docker configuration and pulls
   the selected image.
6. Starts portfolio-backend-candidate on 127.0.0.1:8001.
7. Checks candidate Docker health and the /health response.
8. Archives an existing stopped rollback container under a timestamped name.
9. Stops the serving backend and renames it portfolio-backend-rollback.
10. Starts the new portfolio-backend on port 8000 with restart unless-stopped.
11. Checks the replacement's Docker and local HTTP health.
12. Removes its candidate container and temporary Docker credentials on exit.

The candidate uses production configuration and can access production services.
Avoid checks that change production data.

If the script exits with an error after replacement begins, it attempts to
restore and verify the previous backend. The deployment job still fails.

Automatic rollback does not cover every failure. A timeout, interrupted command,
or application problem missed by /health requires investigation.

## 4. Verify the deployment

Connect through Session Manager and run:

```bash
sudo docker ps -a --filter name=portfolio-backend \
  --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

sudo docker inspect portfolio-backend \
  --format 'Image: {{.Config.Image}} | State: {{.State.Status}} | Health: {{.State.Health.Status}}'

curl --fail --silent --show-error \
  --write-out '\nHTTP %{http_code}\n' \
  http://127.0.0.1:8000/health
```

Expect:

- The image digest matches the GitHub Actions deployment summary.
- State is running and Docker health is healthy.
- The endpoint returns HTTP 200 with {"status":"ok"}.
- The previous backend is retained as a stopped rollback container.

In AWS:

1. Open EC2 > Target Groups > portfolio-backend-tg > Targets.
2. Confirm i-068ba6708472b588f on port 8000 is Healthy.

Open https://www.ericrobinsonjr.com and check the home page,
project details, images, and relevant backend features.

The health endpoint does not verify every feature or database operation.

## 5. Investigate a failed deployment

Read the failed GitHub Actions step and record the SSM command ID if one
was issued.

In AWS, open Systems Manager > Run Command and inspect that command's status
and output.

Connect through Session Manager and inspect the containers using the commands
in section 4.

Common causes include:

- EC2 is stopped or unavailable through Systems Manager.
- IAM permissions or repository variables are incorrect.
- Production configuration is missing or has incorrect permissions.
- The current backend is unhealthy.
- A previous candidate needs review.
- A rollback container is unexpectedly running.
- Image authentication, download, or health checks failed.

Do not assume a failed GitHub job means the previous version is serving.
Verify the actual container image and health.

If GitHub stops waiting or the SSM command times out, inspect both the command
and container state before retrying. The remote command may still be running,
and rollback may need manual attention.

Resolve the cause before retrying the latest intended main run.
Re-running an older run can deploy older code.

Re-running all jobs builds and publishes another image with a new run-attempt
tag. Record the digest from the successful attempt.

## 6. Manual rollback

First confirm no deployment command is still running.

Inspect the containers and identify the previous version. Older rollback
containers may have timestamped names.

Use the commands below only when:

- The replacement is named portfolio-backend.
- The intended previous version is named portfolio-backend-rollback.
- The previous container is stopped.

```bash
sudo docker stop portfolio-backend &&
sudo docker rm portfolio-backend &&
sudo docker rename portfolio-backend-rollback portfolio-backend &&
sudo docker start portfolio-backend
```

If no portfolio-backend container exists, restore the previous container directly:

```bash
sudo docker rename portfolio-backend-rollback portfolio-backend &&
sudo docker start portfolio-backend
```

If automatic rollback already restored the previous backend, verify its image
and health before taking further action.

Repeat local HTTP, Docker, load balancer, and website checks after rollback.

Investigate the faulty release before another deployment. Rolling back the
container does not change main or prevent the next workflow from deploying.

## 7. Cleanup and retention

The script normally removes its candidate container and temporary Docker
credentials.

If a candidate remains after a failure, inspect it and confirm no deployment
is running before removing it.

Keep the latest rollback container stopped during the agreed rollback period.
Retain its image locally and in ECR.

Review timestamped rollback containers and disk usage periodically. Remove
obsolete containers and images only after confirming they are no longer needed.

Stopping EC2 makes the application unavailable and prevents deployments.
Start it and confirm Systems Manager availability before the next main merge.

## Deployment record

For each deployment, record:

- Date and operator
- Commit, GitHub Actions run, and attempt
- Previous and new image digests
- EC2 instance and SSM command ID
- Automated health check results
- Load balancer and website verification
- Whether rollback was attempted and whether recovery succeeded

The first successful automated deployment used commit 35ee5ea,
GitHub Actions run 37263632871, attempt 2.

SSM command: 8b5ac409-41b8-4e56-8b21-381e6fbae203

Deployed image:
327425719636.dkr.ecr.us-east-2.amazonaws.com/portfolio-backend@sha256:79749d7ee51c83272809536a8765135170bbb9e97afef996c5326739c50715a1

Automated container and local HTTP checks passed. The load balancer reported
Healthy, and the website was checked manually.

Manual container rollback was rehearsed during the earlier deployment lesson.