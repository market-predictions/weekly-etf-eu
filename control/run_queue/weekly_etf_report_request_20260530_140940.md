# Weekly ETF report request

requested_at_utc: 2026-05-30T14:09:40Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the executed-report finalization authority overlay.

## Checks requested
- Confirm guarded-auto model execution still passes.
- Confirm final report runtime state keeps official portfolio-state quantities after finalization.
- Confirm scorecard/report enrichment cannot override shares, prices, market values, weights, cash or NAV.
- Validate GLD/GSG row arithmetic in the executed final runtime state and final EN/NL reports.
- This is model-portfolio state handling only, not broker order placement.
