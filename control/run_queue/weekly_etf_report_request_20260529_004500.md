# Weekly ETF report request

requested_at_utc: 2026-05-29T00:45:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue another fresh Weekly ETF Review run after updating the content validator to accept the rotation-aware Final Action Table contract.

## Regression focus
- Confirm the report content validator accepts `rotation_v1` Final Action Table columns.
- Confirm the portfolio rotation plan is built after final lane discovery.
- Confirm runtime state receives the exact `ETF_ROTATION_PLAN_PATH`.
- Confirm Sections 12, 13 and 14 use `rotation_decisions`, `target_weights` and `trade_intents` when present.
- Keep rotation discipline in warning-only mode for this test.
- Continue existing pricing, Dutch quality, bilingual parity, HTML/PDF render and delivery gates.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
