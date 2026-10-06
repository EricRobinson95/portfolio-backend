# Admin security logging

The backend writes JSON security events to stdout using `portfolio.security`.
The serving container's existing Docker `awslogs` configuration delivers these
events to `/portfolio/production/backend`, alongside HTTP request logs.

## Events

| Action | Outcomes | Meaning |
| --- | --- | --- |
| `admin_login` | `success`, `rejected`, `error` | Login returned a token, credentials/input were rejected, or authentication encountered an error. |
| `access_denied` | `rejected` | Another endpoint returned HTTP 401 or 403. This records the response; it does not prove an attack. |
| `admin_password_reset` | `started`, then `success`, `rejected`, or `error` | The operator reset script began, committed the new password, could not find the account, or failed. |

HTTP events carry `request_id` and `status_code`. Match the request ID to the
`http_request` event or the response's `X-Request-ID` header. Reset script events
carry an `operation_id` connecting the start and outcome of one execution.

Unknown usernames and wrong passwords share the `invalid_credentials` reason.
Malformed login input uses `invalid_request`; internal failures use
`authentication_error`. Reasons are fixed codes rather than exception messages.
These security events omit submitted usernames, passwords, password hashes,
tokens, request bodies, and raw headers. HTTP security events include a validated
`client_ip` when available, with `client_ip_source` identifying `peer` or `alb`.
Ordinary HTTP request events omit IP addresses. Operator events have no client IP.

## Trusted client IP configuration

`SECURITY_TRUSTED_PROXY_CIDRS` is a comma-separated list of the actual ALB subnet
CIDRs. Its default is empty: forwarded headers are ignored and only the socket
peer address is recorded. A peer address behind a proxy may identify that proxy,
so check `client_ip_source` before treating it as a visitor address.

Before enabling this in production, verify:

1. The ALB uses `X-Forwarded-For` **Append** mode. Preserve mode is not supported.
2. The EC2 security group permits backend port 8000 only from the ALB security
   group. Trusting a subnet alone does not prove the sender is the ALB.
3. The configured CIDRs match the ALB subnets. Do not use `*`, the entire VPC,
   `0.0.0.0/0`, or `::/0` as a shortcut.
4. Uvicorn runs with `--no-proxy-headers`, as configured in the Dockerfile. For
   local execution, also pass this flag. This preserves the original socket peer
   for our resolver instead of having Uvicorn rewrite it first.

For a trusted connection, the resolver reads only the last address appended by
the ALB, ignoring visitor-supplied prefixes. IPv4, IPv6, and ALB client-port
formats are supported. Missing, duplicate, malformed, or oversized forwarded
headers cause the IP fields to be omitted. Never guess a visitor address from
invalid proxy data. This supports one direct ALB hop; reassess before adding
CloudFront or another proxy in front of the login endpoint.

Set this non-secret configuration through the existing production environment
management process, then recreate the containers. A local `.env` change does
not update `/opt/portfolio/backend.env` or a running container.

The ALB console was checked on 2026-10-05: `portfolio-app-alb` uses Append mode
with client-port preservation off. Its subnets are `subnet-03b38fc52f1aa007a`
(`10.0.1.0/24`) and `subnet-08354f99d440707ee` (`10.0.0.0/24`). Instance
`i-068ba6708472b588f` has security group `sg-0f45adf88548356f8`; its backend TCP
8000 rule permits only ALB security group `sg-057678632c25c0463`. The
corresponding production setting is:

```text
SECURITY_TRUSTED_PROXY_CIDRS=10.0.1.0/24,10.0.0.0/24
```

Recheck these settings if the ALB, network mapping, or security groups change.

IP addresses identify a network source, not a person. Limit log access and retain
them only as long as needed; the current log group has seven-day retention.
This change adds investigation context, not blocking or automated alerts.

## View in CloudWatch

Enter this filter in the log event search bar:

```text
{ $.event = "security_event" }
```

For rejected login attempts:

```text
{ $.event = "security_event" && $.action = "admin_login" && $.outcome = "rejected" }
```

## Password resets and logout

Password reset currently exists only as `scripts/reset_admin_password.py`, using
the configured admin credentials. There is no browser password-reset endpoint.
The script emits security JSON to its own stdout. Running it in a terminal or
through `docker exec` does not automatically send that output through the main
container's logging driver. Central collection for operator executions requires
a separately configured collection path; check that path before relying on
CloudWatch for reset history. Do not run a real reset just to test logging.

Logout currently removes the token from browser session storage; it sends no
backend request, so these logs cannot record it. Logging adds evidence for
investigation; it does not add rate limiting, token revocation, or alerts.
The existing CloudWatch log group retains events for seven days.

## Verification before deployment

Run `python -m pytest -v` in `.venv312` and `git diff --check`.
The security logging tests use isolated authentication dependencies and a fake
reset database; they do not change a real password or connect to production.
After deployment, verify a rejected login produces one security event and one
HTTP request event with matching request IDs. Verify a normal successful admin
login the same way, without copying credentials or tokens into log searches.
