# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T20:47:00Z
requested_run_date: 2026-05-31
mode: phase4_official_exchange_price_observation_evidence_validation

## Purpose

Run the EU bootstrap validation workflow after extending official exchange page evidence with candidate price/date/currency observation text.

## Expected scope

- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Build and validate official exchange source snapshot artifact.
- Build and validate official exchange page evidence artifact.
- Capture candidate price/date/currency snippets as evidence only.
- Keep price_extraction=false.
- Keep valuation_authority=false, funding_authority=false, portfolio_mutation=false, production_delivery=false.
- Keep Twelve Data diagnostic and non-authoritative.
- Validate cash-only EU state and no U.S. ETF holdings.
- Render and validate candidate report skeleton.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_OK
UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
