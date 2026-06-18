# ETF EU Recipient Policy

## Scope

This policy applies to WP14K and any later ETF EU delivery work.

## Current state

```text
real_recipients=false
recipient_activation=false
recipient_source=none
```

## Rules

- WP14K contains no configured recipient list.
- A future recipient list requires a separate explicit policy package.
- Recipients may not be inferred from donor repos, placeholders, workflow defaults, hidden config, or prior report artifacts.
- A delivery-capable workflow may not use recipients until the control layer records a later authorization decision.

## Standing boundary

The presence of rendered HTML, PDF dry-run evidence, or a manifest-like artifact is not recipient approval.
