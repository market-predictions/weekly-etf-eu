# Weekly ETF report request

requested_at_utc: 2026-05-29T01:25:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue a fresh Weekly ETF Review test run after fixing the report/post-render contract layer to consume the exact runtime state and rotation plan.

## Regression focus
- Confirm post-render polish loads the exact runtime state, either via explicit runtime-state path or the latest runtime-state pointer.
- Confirm output-contract fixer consumes the rotation-aware runtime state and no longer falls back to legacy recommendation labels.
- Confirm Section 2 is rotation-aware and does not say no replacement is promoted when trade_intents[] proposes a destination.
- Confirm Section 10 shows the rotation-engine action, especially GLD as Replace partial when applicable.
- Confirm Section 12 is derived from rotation_decisions, not legacy suggested_action labels.
- Confirm Section 14 says Proposed Position Changes / Rotation Trade Intents, not executed changes, while the engine is in warning mode.
- Confirm Section 16 continuity notes the proposed rotation and does not say Reduced: None when trade_intents[] exists.
- Keep rotation discipline in warning-only mode for this test.
- Continue existing pricing, Dutch quality, bilingual parity, HTML/PDF render and delivery gates.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
