# Handover — ETF-EU-MVP19-FIX2 to ETF-EU-MVP20

Date: 2026-07-09
Repository: `market-predictions/weekly-etf-eu`

## Purpose

Continue the Weekly ETF EU Review workflow in a fresh session.

The current objective is to formally close `ETF-EU-MVP19-FIX2` as package-ready and move the roadmap to `ETF-EU-MVP20`.

## Start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
handover/ETF_EU_MVP19_FIX2_TO_MVP20_HANDOVER_20260709.md
```

Then inspect:

```text
output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json
output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
runtime/render_etf_eu_report.py
runtime/render_etf_eu_delivery_package.py
pricing/build_ucits_close_price_validation_basket_results.py
tools/validate_ucits_close_price_validation_basket_results.py
tools/validate_etf_eu_delivery_package_manifest.py
```

## Repository identity

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

`weekly-etf` is architecture/format donor only. Do not copy U.S. holdings, portfolio assumptions, or U.S. instrument authority into EU.

## Current control-file caveat

At the time of this handover, `CURRENT_STATE.md` and `NEXT_ACTIONS.md` still show the previous package as latest completed:

```text
work_package_id=ETF-EU-MVP19-FIX
selected_next_package=ETF-EU-MVP19-FIX2
```

That is stale relative to the evidence now committed. The next session should create a formal `ETF-EU-MVP19-FIX2` closeout artifact and then update the control files.

## Latest committed evidence

Recent commits pushed by the user:

```text
9f6e93b Persist ETF EU MVP19-FIX2 package validation artifacts
0fb9b70 Persist ETF EU MVP19-FIX2 PDF package assets
```

Key files now committed:

```text
output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json
output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
output/weekly_etf_eu_review_260709.md
output/weekly_etf_eu_review_nl_260709.md
output/delivery_package/weekly_etf_eu_review_260709.html
output/delivery_package/weekly_etf_eu_review_260709.pdf
output/delivery_package/weekly_etf_eu_review_nl_260709.html
output/delivery_package/weekly_etf_eu_review_nl_260709.pdf
```

## Evidence summary

UCITS close-price validation basket result:

```text
line_count=11
priced_line_count=10
failed_line_count=1
venue_count=3
currency_count=3
min_threshold_met=true
batch_stopped_for_rate_limit=false
rate_limit_observed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

Package manifest:

```text
client_grade_package_ready=true
pdf_output_available=true
html_output_available=true
dutch_primary=true
english_companion=true
main_surface_tbd_candidate_exposure=false
main_surface_us_proxy_exposure=false
nan_price_in_client_surface=false
stale_delivery_wording_present=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
```

## Fixes completed

Yahoo/yfinance basket runner:

```text
pricing/build_ucits_close_price_validation_basket_results.py
tools/validate_ucits_close_price_validation_basket_results.py
```

Current behavior:

```text
requests_are_serialized=true
pause_seconds_between_symbols=15.0
rate_limit_mode=stop
batch stops gracefully if Yahoo returns a rate-limit error
remaining rows are recorded as skipped rather than retried aggressively
```

Client-surface finite-close hygiene:

```text
runtime/render_etf_eu_report.py
```

Current behavior:

```text
None, NaN, infinite, and non-positive close values are not printed as client-facing prices.
```

## Required next package

Create formal closeout for `ETF-EU-MVP19-FIX2`:

```text
control/ETF_EU_MVP19_FIX2_READY_FOR_CONTROLLED_RESEND_V1.md
output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json
output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_notes_20260709_000000.md
tools/validate_etf_eu_mvp19_fix2_ready_for_controlled_resend.py
tests/test_etf_eu_mvp19_fix2_ready_for_controlled_resend.py
control/decisions/ETF_EU_MVP19_FIX2_READY_FOR_CONTROLLED_RESEND_DECISION_20260709.md
```

Target state after closeout:

```text
work_package_id=ETF-EU-MVP19-FIX2
status=completed_client_grade_package_ready_for_controlled_resend
source_work_package=ETF-EU-MVP19-FIX
client_grade_package_ready=true
pdf_output_available=true
actual_close_fetch_completed=true
ucits_close_price_validation_line_count=11
ucits_close_price_validation_priced_line_count=10
ucits_close_price_validation_venue_count=3
ucits_close_price_validation_currency_count=3
resend_performed=false
delivery_success_closed=false
receipt_confirmed=false
completion_claimed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=client_grade_package_ready_for_controlled_resend
selected_next_package=ETF-EU-MVP20
```

## Validation commands for next session

```bash
git pull --ff-only origin main
git status --short

python tools/validate_ucits_close_price_validation_basket_results.py \
  --artifact output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json

python tools/validate_etf_eu_delivery_package_manifest.py \
  --manifest output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
```

## Fresh-chat starter prompt

```text
You are working in market-predictions/weekly-etf-eu.

Read first:
1. control/SYSTEM_INDEX.md
2. control/CURRENT_STATE.md
3. control/NEXT_ACTIONS.md
4. handover/ETF_EU_MVP19_FIX2_TO_MVP20_HANDOVER_20260709.md

Task:
Close ETF-EU-MVP19-FIX2 formally as client_grade_package_ready_for_controlled_resend, update CURRENT_STATE.md and NEXT_ACTIONS.md, then prepare ETF-EU-MVP20 instructions. Do not execute the next guarded transport step unless explicitly instructed.
```
