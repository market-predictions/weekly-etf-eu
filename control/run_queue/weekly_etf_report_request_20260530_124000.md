# Weekly ETF report request

requested_at_utc: 2026-05-30T12:40:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run.

## Checks requested
- Use official portfolio state as the execution authority for shares and market value.
- Do not let stale scorecard memory override executed position quantities.
- Confirm model execution no longer fails with NAV drift from stale GLD share count.
- Confirm model portfolio state, trade ledger, Section 14, and Section 15 reconcile before delivery.
- This is model-portfolio state handling only, not broker order placement.
