# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T15:30:00Z
requested_run_date: 2026-05-31
mode: phase4_twelve_data_symbol_discovery_validation

## Purpose

Run the EU bootstrap validation workflow after adding Twelve Data UCITS provider-symbol discovery.

## Expected scope

- Validate EU control and config files.
- Validate UCITS registry and investability contract.
- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Build and validate Twelve Data symbol-discovery artifact.
- Preserve all source-discovery evidence as diagnostic only.
- Keep `accept_as_valuation_grade=false` and `valuation_grade_row_count=0`.
- Validate cash-only EU state and no U.S. ETF holdings.
- Render and validate candidate report skeleton.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected markers

```text
UCITS_TWELVE_DATA_SYMBOL_DISCOVERY_OK
UCITS_TWELVE_DATA_SYMBOL_DISCOVERY_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```
