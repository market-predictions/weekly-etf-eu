# Weekly ETF report request

requested_at_utc: 2026-05-29T02:50:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue a fresh Weekly ETF Review run after adding a pre-validation client-surface scrub to the ETF content contract.

## Regression focus
- Confirm client-surface scrub removes residual internal snake-case labels before content validation.
- Confirm Section 2 no longer exposes rotation_decisions, target_weights or trade_intents as raw labels.
- Confirm Section 7 no longer exposes output/etf_valuation_history.csv as raw plumbing.
- Confirm Section 10 no longer exposes churn_budget_used as a raw override code.
- Confirm Section 11 no longer contains double-negative reduction wording.
- Confirm Final Action Table still uses client-facing Decision rationale / Toelichting.
- Confirm proposed rotation intent remains proposed and not executed while warning mode is active.
- Confirm actual holdings remain separate from proposed trade intents until a model-execution layer is explicitly enabled.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
