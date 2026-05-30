# Weekly ETF report request

requested_at_utc: 2026-05-30T13:44:04Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review run after the execution-state authority validator patch.

## Checks requested
- Use official portfolio state as the execution authority for shares, cash, NAV and market values.
- Run the new execution-state authority validator before delivery.
- Block delivery if any holding row mixes stale shares with post-execution market values.
- Confirm GLD/GSG row arithmetic reconciles: shares × local price = local market value, local market value / FX = EUR market value, EUR market value / NAV = weight.
- Confirm guarded-auto execution finalization rebuilds the final EN/NL reports from executed portfolio state.
- This is model-portfolio state handling only, not broker order placement.
