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
tokens, request bodies, headers, and visitor IP addresses.

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
