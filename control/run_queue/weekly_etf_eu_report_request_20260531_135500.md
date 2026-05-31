# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-31T13:55:00Z
requested_run_date: 2026-05-31
mode: phase4_valuation_pricing_validation

## Purpose

Run the EU bootstrap validation workflow after adding Phase 4 valuation-pricing authority preparation.

## Expected scope

- Validate EU control files.
- Validate EU config files.
- Validate UCITS registry and investability contract.
- Build and validate UCITS pricing candidates.
- Run non-authoritative UCITS pricing preflight.
- Build and validate UCITS valuation pricing artifact.
- Validate cash-only EU state and no U.S. ETF holdings.
- Render and validate candidate report skeleton.
- Confirm no portfolio mutation, no PDF generation and no email delivery.

## Expected Phase 4 markers

```text
UCITS_VALUATION_PRICING_POLICY_OK
UCITS_VALUATION_PRICES_OK
UCITS_VALUATION_PRICES_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```
