# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T21:55:00Z
requested_run_date: 2026-05-31
mode: phase4_deutsche_boerse_adapter_candidate_close_validation

## Purpose

Run the EU bootstrap validation workflow after implementing the first non-authoritative Deutsche Boerse / Xetra close adapter parser behind the generic close-price engine interface.

## Expected scope

- Build and validate generic UCITS close observations.
- Deutsche Boerse adapter may emit candidate_close as unverified evidence if a plausible clean candidate is parsed.
- Candidate close must remain non-authoritative.
- completed_session must remain false.
- valuation_authority=false, funding_authority=false, portfolio_mutation=false, production_delivery=false.
- Euronext adapter remains scaffold-only pending stable endpoint integration.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

UCITS_CLOSE_OBSERVATIONS_OK
UCITS_CLOSE_OBSERVATIONS_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
