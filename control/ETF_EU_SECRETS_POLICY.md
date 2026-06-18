# ETF EU Secrets Policy

## Scope

This policy applies to WP14K and later ETF EU delivery authorization work.

## Current state

```text
secrets_required_for_this_package=false
secrets_present=false
mail_transport_enabled=false
smtp_configured=false
```

## Rules

- WP14K requires no delivery secret.
- WP14K enables no SMTP or outbound mail transport.
- Do not add app passwords, API tokens, SMTP credentials, or delivery secrets in this package.
- Any future delivery secret must be handled through a separate authorization package and must not be embedded in report artifacts.

## Standing boundary

A render dry-run or policy artifact is not permission to configure a mail transport.
