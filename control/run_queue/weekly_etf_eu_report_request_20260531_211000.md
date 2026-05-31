# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T21:10:00Z
requested_run_date: 2026-05-31
mode: phase4_structured_official_page_observation_validation

## Purpose

Run the EU bootstrap validation workflow after adding source-specific structured official page observations.

## Expected scope

- Build and validate official exchange page evidence artifact.
- Include structured_candidate_observation per official source.
- Euronext: record endpoint hints and product code presence only.
- Deutsche Boerse: record label windows for Schlusspreis des letzten Handelstages, Handelswaehrung, and Letzter Preis.
- Keep candidate_close and candidate_date null until a clean parser validator exists.
- Keep price_extraction=false.
- Keep valuation_authority=false, funding_authority=false, portfolio_mutation=false, production_delivery=false.
- Validate cash-only EU state and no U.S. ETF holdings.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_OK
UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
