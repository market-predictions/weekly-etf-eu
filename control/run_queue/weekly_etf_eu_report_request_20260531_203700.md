# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T20:37:00Z
requested_run_date: 2026-05-31
mode: phase4_official_exchange_page_evidence_validation

## Purpose

Run the EU bootstrap validation workflow after adding official exchange page evidence artifacts.

## Expected scope

- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Build and validate official exchange source snapshot artifact.
- Build and validate official exchange page evidence artifact.
- Keep page evidence identity-only; do not extract or promote prices.
- Keep all authority flags false.
- Keep Twelve Data diagnostic and non-authoritative.
- Validate cash-only EU state and no U.S. ETF holdings.
- Render and validate candidate report skeleton.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_OK
UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
