# Weekly ETF report request

requested_at_utc: 2026-05-30T18:46:00Z
requested_run_date: 2026-05-30
mode: pro
requested_close_date:
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## Request
Queue a fresh Weekly ETF Review verification run after the max-position action cap delivery guard.

## Verification focus
- Confirm SMH is not shown as Add / destination while its current weight is above the 25% max-position cap.
- Confirm SMH is described as best earned exposure but no fresh capital while above cap.
- Confirm delivery HTML/PDF validation fails if any over-cap ticker appears as Add.
- Confirm GLD/GSG holdings remain arithmetically reconciled.
- Confirm already-executed GLD to GSG rotation remains no-op and post-execution wording remains clean.
- Confirm equity curve remains based on repaired canonical valuation history and does not inflate.
- Confirm final English and Dutch reports pass render and delivery validators.
