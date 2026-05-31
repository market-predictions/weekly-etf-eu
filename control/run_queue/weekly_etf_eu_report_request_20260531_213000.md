# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T21:30:00Z
requested_run_date: 2026-05-31
mode: phase4_generic_close_price_engine_scaffold_validation

## Purpose

Run the EU bootstrap validation workflow after adding the generic UCITS close-price engine scaffold.

## Expected scope

- Validate EU control/config files.
- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Build official exchange source snapshot and page evidence artifacts.
- Build and validate generic UCITS close observations.
- Keep adapter outputs scaffold-only.
- Keep candidate_close=null and candidate_date=null.
- Keep completed_session=false.
- Keep valuation_authority=false, funding_authority=false, portfolio_mutation=false, production_delivery=false.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

UCITS_CLOSE_OBSERVATIONS_OK
UCITS_CLOSE_OBSERVATIONS_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
