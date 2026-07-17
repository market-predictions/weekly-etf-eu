# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-07-17
repository=market-predictions/weekly-etf-eu
operating_mode=routine_production_with_three_position_active_model_portfolio
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
selected_next_action=DISPATCH_AND_VERIFY_CORRECTED_VISUAL_PREVIEW_20260717_123500
```

## Latest completed delivery

```text
work_package_id=ETF-EU-RUN260712-FIX2B_CORRECTED_RESEND_RECEIPT_CLOSEOUT
report_date=2026-07-12
github_workflow_run_id=29428021408
receipt_confirmed=true
production_delivery_cycle_closed=true
```

This remains the latest completed email-delivery cycle. No 2026-07-17 preview performed transport or email delivery.

## Active broker-neutral model portfolio

```text
starting_capital_eur=100000.00
nav_eur=100016.60
cash_eur=60439.44
invested_market_value_eur=39577.16
cash_weight_pct=60.4294
position_count=3
model_portfolio_only=true
real_broker_execution=false
```

| Position | ISIN | Shares | Model price | Market value | Weight | Current status |
|---|---|---:|---:|---:|---:|---|
| VWCE | IE00BK5BQT80 | 151 | €165.32 | €24,963.32 | 24.959177% | Funded global-core first tranche |
| EUNA | IE00BDBRDM35 | 1,526 | €4.913 | €7,497.24 | 7.495996% | Funded aggregate-bond first tranche |
| SXR8 | IE00B5BMR087 | 10 | €711.66 | €7,116.60 | 7.115419% | Hold; no second tranche authorised |

Cash plus invested market value reconciles exactly to NAV at eurocent precision.

## Preview run 20260717_114500

```text
github_workflow_run_id=29571969253
workflow=ETF EU - Generate and Validate Preview (NO EMAIL)
workflow_result=success
machine_validation_passed=true
dutch_page_count=6
english_page_count=6
visual_review_passed=false
client_grade_preview_accepted=false
status=machine_validated_but_rejected_by_visual_review
superseded=true
superseded_by_run_id=20260717_123500
```

Machine validation passed with no blockers and confirmed all three funded ISINs in Dutch and English HTML/PDF. The complete preview nevertheless remains rejected because visual review found:

1. overlapping adjacent date labels at the right edge of the equity curve;
2. aggressive wrapping of ticker, ISIN, price and date cells in the funded-position table;
3. an English valuation-history comment in the Dutch report.

Authoritative evidence:

```text
output/quality/etf_eu_client_grade_v2_validation_20260717_114500.json
output/quality/etf_eu_routine_pdf_visual_review_20260717_114500.json
output/run_manifests/etf_eu_routine_preview_manifest_20260717_114500.json
```

The HTML/PDF files for suffix `260717_04` are historical preview evidence only and must not be delivered.

## Implemented visual correction

```text
equity_tick_spacing_commit=ada050751f8a3084bf02acacacc71ab97c19d190
funded_table_and_localization_commit=2ed921e440de336d92d1edd0a11d7b88d455016b
visual_regression_test_commit=5a07084d3249d508dd6c2d6acf74cf946a163a9a
```

The corrected output contract now:

- suppresses intermediate equity-curve ticks when date labels cannot meet a minimum spacing;
- preserves and edge-aligns the first and last curve dates;
- applies fixed column widths and nowrap rules to funded identifiers and numeric fields;
- improves pricing-table identifier/date handling;
- uses language-aware hyphenation for wide tables;
- localizes the Dutch valuation-history comment;
- retains the visible funded ISIN identity strip.

The implementation adapts the upstream `weekly-etf` SVG contract but intentionally adds collision avoidance because the donor implementation uses fixed representative ticks without a spacing gate.

## Corrected preview queue

```text
run_id=20260717_123500
report_date=2026-07-17
report_suffix=260717_05
queue_path=control/run_queue/etf_eu_routine_preview_request_20260717_123500.md
workflow=.github/workflows/run-weekly-etf-eu-routine-preview.yml
execution_mode=generate_validate_only
status=queued_not_executed
workflow_run_verified=false
production_delivery_authority=false
```

The connector-authored queue push did not create a verifiable GitHub Actions run. One manual workflow dispatch is the only remaining external action.

## Authority boundaries

```text
canonical_identity=isin_plus_exact_share_class_plus_venue_plus_exchange_line_plus_currency
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
model_portfolio_only=true
real_broker_execution=false
valuation_grade=false
portfolio_mutation=false
production_delivery_authority=false
transport_attempted=false
send_executed=false
```

## Four-layer status

### Decision framework

Review VWCE, EUNA and SXR8 independently for role validity, contribution, overlap and invalidation. No automatic add, reduction, exit, second tranche or satellite activation is allowed.

### Input/state contract

```text
config/ucits_symbol_registry.yml
config/ucits_close_price_validation_basket.yml
config/etf_eu_target_allocation.yml
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
output/etf_eu_valuation_history.csv
```

### Output contract

The corrected report must visibly and consistently show all three funded positions, cash, exact UCITS identities, whole-share quantities, pricing dates, current weights, contribution, overlap and a non-overlapping equity curve. Dutch is primary; English is companion.

### Operational runbook

```text
manual dispatch corrected preview 20260717_123500
→ focused funded-aware and visual-contract regression tests
→ fresh UCITS pricing and macro refresh
→ normalized funded-aware state
→ Dutch and English HTML/PDF
→ strict funded-state and ISIN consistency gates
→ complete page review
→ visual-review manifest
→ no delivery without separate explicit authority
```
