# ETF EU Accepted-Package Immutable Delivery Decision — 2026-07-17

## Decision

A client-grade report may be transported only from the exact Dutch and English HTML/PDF bytes that passed both machine validation and complete visual review.

For run `20260717_141500`, the authoritative delivery package is locked by:

```text
output/delivery_control/etf_eu_accepted_package_lock_20260717_141500.json
```

The lock contains the Git blob identity of exactly four client files. The delivery queue validator recalculates those identities before transport. Any byte change blocks delivery.

## Layer separation

### Decision framework

The portfolio decision remains unchanged. VWCE, EUNA and SXR8 are active model positions; no new allocation or portfolio mutation is authorised by delivery.

### Input/state contract

The accepted report identity is `run_id=20260717_141500`, `report_date=2026-07-17`, `report_suffix=260717_06`.

### Output contract

The locked files are the Dutch-primary and English-companion HTML/PDF outputs that passed the strict machine gate and the twelve-page visual review.

### Operational runbook

Delivery consumes the accepted package only. It must not refresh pricing, rebuild normalized state, rerender HTML/PDF or mutate the portfolio before transport.

## Authority boundary

```text
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
receipt_confirmed=false
```

Transport success is not inbox receipt. Production delivery closes only after independent mailbox confirmation.

## Idempotency

Before a live transport attempt, the workflow searches existing current-package transport results. A prior successful result for the same queue and report suffix blocks a duplicate send.

## Connector boundary

Repository preparation may be automated, but the connector security boundary does not create an automatically triggering live-send queue. The final live action therefore remains an explicit GitHub `workflow_dispatch` with guarded-send confirmation.
