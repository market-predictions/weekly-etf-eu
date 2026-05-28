# Weekly ETF report request

requested_at_utc: 2026-05-29T00:15:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue one fresh Weekly ETF Review run to test the full rotation-engine path end to end.

## Regression focus
- Run persistent ETF pricing first and persist the exact pricing audit path.
- Run lane discovery and challenger pricing.
- Build the ETF portfolio rotation plan after final lane discovery.
- Validate the rotation output contract.
- Run rotation discipline in warning-only mode.
- Build runtime ETF state using the exact rotation plan path.
- Render EN/NL reports from the same runtime state and same rotation artifact.
- Confirm sections 12, 13 and 14 consume rotation_decisions, target_weights and trade_intents when present.
- Continue existing pricing, Dutch quality, bilingual parity, HTML/PDF render and delivery gates.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
