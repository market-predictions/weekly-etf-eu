# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T15:15:00Z
requested_run_date: 2026-05-31
mode: phase4_twelve_data_candidate_source_validation

## Purpose

Run the EU bootstrap validation workflow after integrating Twelve Data as candidate valuation evidence source.

## Expected scope

- Validate EU control files.
- Validate EU config files.
- Validate UCITS registry and investability contract.
- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Capture Twelve Data candidate evidence when the repository secret and provider symbols resolve.
- Keep `accept_as_valuation_grade=false` and `valuation_grade_row_count=0`.
- Validate cash-only EU state and no U.S. ETF holdings.
- Render and validate candidate report skeleton.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

```text
UCITS_VALUATION_PRICING_POLICY_OK
UCITS_VALUATION_PRICES_OK
UCITS_VALUATION_PRICES_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```
