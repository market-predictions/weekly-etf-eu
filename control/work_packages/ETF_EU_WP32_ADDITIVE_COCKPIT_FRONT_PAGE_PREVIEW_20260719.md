# ETF-EU-WP32 — Additive cockpit front-page preview

Date: 2026-07-19
Status: completed and validated
Branch: `feature/etf-eu-wp32-additive-cockpit-preview`
Pull request: #61

## Purpose

Add one EU/UCITS cockpit page before the existing investor and analyst reports while preserving the current evidence body.

## Donor adaptation

Adapted from `market-predictions/weekly-etf`:

- normalized-state derivation;
- one additive page;
- explicit feature gate and classic fallback;
- inline/table email rendering;
- existing report body preserved;
- implementation separated from later promotion.

EU authority remains Dutch-primary, ISIN-first, UCITS-first and EUR-based.

## Final validation

```text
validation_run=29666911258
regression_tests_passed=true
machine_validation_passed=true
protected_inputs_unchanged=true
NL_page_count=7
EN_page_count=7
classic_page_count=6
page_delta=1
classic_sections_preserved=15
primary_visual_review_passed=true
secondary_adversarial_review_passed=true
blockers=0
```

## Review corrections

1. inline suppression prevents a duplicate summary in email clients;
2. the small positive return is shown at two-decimal precision;
3. drawdown context states the three-point valuation-history depth.

## Boundaries

```text
preview_only=true
production_enablement=false
client_package_unchanged=true
portfolio_state_unchanged=true
pricing_state_unchanged=true
```

## Handover

`control/handovers/HANDOVER_ETF_EU_WP32_ADDITIVE_COCKPIT_FRONT_PAGE_PREVIEW_20260719.md`

## Next package

`ETF-EU-WP33_COCKPIT_FRONT_PAGE_PRODUCTION_ENABLEMENT`
