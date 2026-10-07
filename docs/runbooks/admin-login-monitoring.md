# Admin login metrics, alerts, and dashboard

## Purpose and flow

This monitoring identifies a burst of rejected admin logins and sends an email
so an operator can investigate. It does not block requests or identify a person.

```text
Admin login security event
  -> CloudWatch Logs metric filter
  -> RejectedAdminLogins metric
  -> CloudWatch alarm
  -> SNS topic -> confirmed email subscription

Dashboard -> metric history and current alarm status
```

The source of configuration is `infra/cloudwatch.yaml`, applied to the
`portfolio-backend-observability` stack in **us-east-2**. This guide describes
the template in the repository; check the deployed stack when investigating
configuration drift.

## Resources and settings

| Resource | Configuration |
| --- | --- |
| Log group | `/portfolio/production/backend`, seven-day retention. |
| Metric filter logical ID | `RejectedAdminLoginsFilter`. |
| Metric namespace | `Portfolio/Backend`. |
| Metric name | `RejectedAdminLogins`. |
| Metric value and unit | Each matching event contributes `1`, unit Count. |
| Alarm name | `portfolio-production-rejected-admin-logins`. |
| Alarm statistic and period | Sum over 60 seconds. |
| Threshold | Greater than or equal to 5. |
| Evaluation | One breaching data point out of one evaluation period. |
| Missing data | `notBreaching`. |
| SNS topic | `portfolio-production-admin-security-alerts`. |
| Subscription | Email endpoint supplied by the `AlertEmail` stack parameter. |
| Dashboard | `portfolio-production-admin-security`. |

## What is counted and why

The filter pattern is:

```text
{ $.event = "security_event" && $.action = "admin_login" && $.outcome = "rejected" }
```

`&&` means all three conditions must match. Each matching security event adds
one to the metric. The HTTP request event for the same login is excluded, so
these two different event types do not double-count a login.

The application marks wrong credentials and malformed login input as rejected.
Consequently, both can contribute to this metric. Successful logins,
authentication errors, other access-denied events, password resets, and health
checks do not match this pattern.

The metric has no dimensions: it combines matching events across all clients
and all streams in this log group. It is not a per-IP counter. The filter has
no default value, so periods without matches can have missing data rather than
an explicit zero. Metric filters process new events after creation and do not
backfill existing logs. AWS also documents at-least-once delivery with occasional
duplicates, so counts are operational signals rather than an exact audit ledger.
See [AWS metric filter behavior](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/MonitoringLogData.html).

Use **Sum**, not Average, to see the count per minute. For example, three matching
events in one minute and four in the next produce values 3 and 4. Neither
minute reaches the threshold; the alarm does not sum those minutes into 7.
These are metric periods, not a rolling 60-second window starting at the first
login. Attempts crossing a minute boundary can be split between periods.

## Alarm and email behavior

When evaluation determines that a one-minute Sum is at least 5, the alarm can
enter ALARM and publish to SNS. The email subscription must be confirmed before
it can receive notifications. The template configures `AlarmActions` but no
`OKActions`, so recovery does not send an OK email.

SNS alarm notifications occur on transitions into ALARM rather than once per
rejected login or repeatedly while the alarm stays in ALARM. Allow for ingestion,
evaluation, and delivery time. See [CloudWatch alarm behavior](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html).

After the burst ends, later evaluations can return the alarm to OK. Because
missing data is treated as non-breaching, OK can also occur while the backend
is stopped or logs are not arriving. Verify recent log delivery separately;
OK does not prove the application or monitoring pipeline is healthy.

## Viewing and investigating

1. Open CloudWatch in us-east-2 and select dashboard
   `portfolio-production-admin-security`.
2. The metric widget shows Sum with a 60-second period; the default dashboard
   range is the past six hours. The alarm widget shows its current state.
3. Open the alarm's history and note the breaching period and state-change time.
4. Search the log group for rejected admin login events using the filter above,
   with a matching time range. Search all relevant container streams.
5. Compare reasons, request IDs, and validated `client_ip`/`client_ip_source`
   fields. See the security logging guide for the Cloudflare and ALB trust chain.
6. Check whether attempts were an intentional exercise, ordinary mistakes,
   malformed requests, or unexpected repeated activity. The threshold alone
   does not establish brute force or account compromise.
7. If activity is unexpected, assess impact and choose a reviewed response,
   such as an appropriate Cloudflare rule or application rate limit. Those
   protections are separate changes; this alarm does not implement them.

To view accepted and rejected logins together:

```text
{ $.event = "security_event" && $.action = "admin_login" && ($.outcome = "success" || $.outcome = "rejected") }
```

For authentication failures needing application investigation:

```text
{ $.event = "security_event" && $.action = "admin_login" && $.outcome = "error" }
```

If no metric appears, confirm new matching events arrived after filter creation,
and verify the namespace, name, region, time range, Sum statistic, and period.
If ALARM occurs without email, inspect alarm action history, action enablement,
the SNS topic reference, subscription confirmation, and the recipient's spam
folder. A missing email does not mean no alarm occurred.

## Controlled verification

The lesson already exercised rejected logins, an ALARM email, a red dashboard
alarm widget, and recovery to OK. That is historical verification, not a claim
about the current live state.

For an authorized repeat test, confirm the backend is running and the SNS
subscription is confirmed. Use deliberately incorrect test credentials on your
own admin login, keeping at least five rejections within one metric minute.
Do not expose a real password or perform an actual password reset for this test.
Inspect logs and the metric, then confirm the state transition and email.
Stop the attempts and observe later recovery; there is no recovery email action.

Manually forcing an alarm state tests a different part of the system and does
not verify log ingestion or the metric filter.

## Changing configuration

1. Edit `infra/cloudwatch.yaml` on a feature branch and run `git diff --check`.
2. Create a CloudFormation change set using the updated template. Keep the
   intended EC2 role and confirmed email endpoint in the parameters.
3. Review proposed resource additions, modifications, and replacements before
   executing. Investigate unrelated replacements rather than executing blindly.
4. Execute the reviewed change set and wait for the stack update to complete.
5. Verify the deployed settings and behavior, then preserve the reviewed change
   in Git through the normal pull request flow.

Uploading a template supplies CloudFormation with the desired configuration.
Creating a change set previews it; executing the change set applies it. A Git
commit or push alone does not update this stack. Console edits outside the
template can create drift and may be overwritten by later stack updates.

## Costs

Creating these Markdown guides costs no AWS usage. Running the monitoring can
incur charges for the custom metric, alarm, dashboard, log ingestion/storage,
and SNS requests/email deliveries, depending on account allowances and usage.
EC2, ALB, and database charges are separate. Stopping EC2 does not remove
monitoring resources or guarantee that all AWS charges stop.

Check [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/) and
[SNS pricing](https://aws.amazon.com/sns/pricing/) before adding resources or
increasing usage. Avoid adding client IP as a metric dimension without reviewing
privacy and cost: many unique values can create many distinct metrics.

## Related guides

- [HTTP request logging](http-request-logging.md)
- [Admin security logging](admin-security-logging.md)
- [Request tracing](request-tracing.md)
