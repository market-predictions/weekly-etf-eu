# Weekly ETF report request

requested_at_utc: 2026-05-29T15:15:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue a fresh Weekly ETF Review run after enabling guarded auto model execution.

## Regression focus
- Confirm shadow model-execution artifact is still built and validated from runtime trade_intents.
- Confirm guarded_auto model execution writes official model trade-ledger rows when all hard gates pass.
- Confirm guarded_auto updates output/etf_portfolio_state.json with post-trade model holdings.
- Confirm GLD -> GSG, if still selected by generic rules, becomes official model-portfolio execution rather than only a recommendation.
- Confirm no execution occurs if pricing, source holding, destination pricing, max turnover, max source reduction, or NAV drift gates fail.
- Confirm next run starts from the updated official portfolio state, not from stale pre-trade holdings.
- Confirm this remains model execution only and does not imply broker execution.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
