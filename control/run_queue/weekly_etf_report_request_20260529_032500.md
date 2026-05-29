# Weekly ETF report request

requested_at_utc: 2026-05-29T03:25:00Z
requested_run_date: 2026-05-29
mode: pro
requested_close_date: 
pricing_basis_requested: latest completed U.S. regular-session close available at runtime
strict_fresh_pricing_required: false
pricing_tolerance_policy: balanced

## User request
Queue a fresh Weekly ETF Review run after fixing the client-surface validator import path.

## Regression focus
- Confirm tools/validate_etf_client_surface_clean.py can import runtime.scrub_etf_client_surface from the repository root.
- Confirm validator remains scoped to the current EN/NL report pair plus matching delivery HTML only.
- Confirm current report pair is scrubbed before client-surface validation.
- Confirm no raw internal snake_case labels remain in the current EN/NL report pair or matching delivery HTML.
- Confirm prose does not use double-negative reduction wording.
- Confirm proposed rotation intent remains proposed and not executed while warning mode is active.

## Fresh-pricing requirements
- Use latest completed U.S. regular-session close available at runtime.
- Reprice current holdings per ticker.
- Balanced tolerance is allowed: one low-to-moderate-weight prior-valid close may be tolerated if the rest of the current portfolio is exact-close priced and no holding is unresolved/carried forward.
- Fail loud if pricing coverage is weak, if unresolved/carried-forward holdings remain, or if Section 7 does not reconcile with Section 15.
