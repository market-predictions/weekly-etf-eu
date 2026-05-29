# Weekly ETF report request

requested_at_utc: 2026-05-29T01:05:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue one more fresh Weekly ETF Review test run after changing Section 14 language from executed position changes to proposed rotation trade intents.

## Regression focus
- Confirm Section 14 no longer implies execution while the rotation engine is still in warning mode.
- Confirm English Section 14 uses `Proposed Position Changes / Rotation Trade Intents` when `trade_intents[]` exists.
- Confirm Dutch Section 14 uses `Voorgestelde positiewijzigingen / rotatie-intenties` when `trade_intents[]` exists.
- Confirm continuity wording no longer says `Reduced: None` when a proposed rotation intent exists.
- Confirm the report content validator accepts the proposed-intent Section 14 title.
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
