# ETF EU Delivery Authorization Gate

## Scope

This gate controls whether ETF EU output may ever move from render dry-run evidence to send-capable delivery.

## Current state

```text
delivery_authorized=false
production_delivery=false
proof_claimed=false
real_receipt=false
send_attempted=false
```

## Rules

- Production delivery remains blocked.
- A dry-run render manifest is not a delivery receipt.
- A future delivery success claim requires a real receipt or manifest path designed for that purpose.
- Delivery cannot be authorized by code alone.
- A later package must explicitly record `delivery_authorized=true` in the control layer before any send-capable workflow may be enabled.

## Standing boundary

WP14K is a policy gate. It creates no outbound action and no delivery authority.
