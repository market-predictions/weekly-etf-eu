# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T16:55:00Z
requested_run_date: 2026-05-31
mode: phase4_official_exchange_source_snapshot_validation

## Purpose

Run the EU bootstrap validation workflow after the source-policy pivot away from Twelve Data as primary authority path and after adding official exchange source snapshot artifacts.

## Expected scope

- Validate EU control and config files.
- Validate UCITS registry and investability contract.
- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Build and validate official exchange source snapshot artifact.
- Keep Twelve Data diagnostic and non-authoritative.
- Keep all authority flags false.
- Validate cash-only EU state and no U.S. ETF holdings.
- Render and validate candidate report skeleton.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

UCITS_VALUATION_PRICING_POLICY_OK
UCITS_VALUATION_PRICES_OK
UCITS_VALUATION_PRICES_VALIDATION_OK
UCITS_OFFICIAL_EXCHANGE_SOURCE_SNAPSHOT_OK
UCITS_OFFICIAL_EXCHANGE_SOURCE_SNAPSHOT_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
