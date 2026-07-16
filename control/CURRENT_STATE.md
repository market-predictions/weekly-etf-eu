# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-07-17
repository=market-predictions/weekly-etf-eu
operating_mode=routine_production_with_three_position_active_model_portfolio
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
selected_next_action=RUN_CORRECTED_THREE_POSITION_NON_DELIVERY_PREVIEW_20260717_005500
```

## Latest completed delivery

```text
work_package_id=ETF-EU-RUN260712-FIX2B_CORRECTED_RESEND_RECEIPT_CLOSEOUT
report_date=2026-07-12
github_workflow_run_id=29428021408
receipt_confirmed=true
production_delivery_cycle_closed=true
```

This remains the latest completed email-delivery cycle. No 2026-07-16 or 2026-07-17 preview run performed transport or email delivery.

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

## Preview run 20260716_214500

```text
workflow=ETF EU - Generate and Validate Preview (NO EMAIL)
workflow_result=success
machine_validation_passed=true
dutch_page_count=6
english_page_count=6
visual_review_passed=false
content_consistency_passed=false
status=machine_validated_but_rejected_by_content_and_visual_review
superseded=true
superseded_by_run_id=20260717_005500
```

Machine validation passed, but the report was not accepted because the funded portfolio and client narrative conflicted. The rejected package:

- described only one active model position while the portfolio contained VWCE, EUNA and SXR8;
- described funded VWCE and EUNA lanes as not funded or still awaiting already-closed verification gates;
- retained broker-availability wording in model-investability copy;
- retained stale next-run instructions;
- omitted pricing dates from the funded-position table.

Authoritative review evidence:

```text
output/quality/etf_eu_routine_pdf_visual_review_20260716_214500.json
output/run_manifests/etf_eu_routine_preview_manifest_20260716_214500.json
```

The rejected HTML/PDF files are historical preview evidence only and must not be delivered or promoted.

## Implemented repair

```text
renderer_repair_commit=56e10fd45a4cac5e4ebd8883e97c20bc6876a300
validator_repair_commit=320afd5d97f68d14c3883c0ae6e98fc3d445d8f1
regression_test_commit=f4ff86adf8b3fb4b0b9be11d9d0ce42977091b04
preview_contract_commit=b7ff878d8a05f24cfc844f80f680f36643cde127
```

The funded-aware renderer now:

- reconciles all three funded positions;
- marks VWCE, EUNA and SXR8 opportunity lanes as active funded model positions;
- separates active core/bond positions from unfunded satellites;
- removes broker-specific model gates;
- renders dynamic plural cockpit and conclusion copy;
- includes position pricing dates;
- updates overlap, contribution and next-run language.

The strict client-grade validator now fails on funded-state contradictions, singular one-position copy, broker-dependent model wording and stale funded-lane statuses. Regression tests cover the three-position state.

## Corrected preview queue

```text
run_id=20260717_005500
report_date=2026-07-17
report_suffix=260717
queue_path=control/run_queue/etf_eu_routine_preview_request_20260717_005500.md
workflow=.github/workflows/run-weekly-etf-eu-routine-preview.yml
execution_mode=generate_validate_only
status=queued_not_executed
workflow_run_verified=false
production_delivery_authority=false
```

The connector-authored queue push did not create a verifiable GitHub Actions run. Manual workflow dispatch is therefore the only remaining external action.

## Authority boundaries

```text
canonical_identity=isin_plus_exact_share_class_plus_venue_plus_exchange_line_plus_currency
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
model_portfolio_only=true
real_broker_execution=false
valuation_grade=false
production_delivery_authority=false
```

No portfolio mutation, real broker order, transport or email send is authorised by the corrected preview cycle.

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

The corrected report must visibly and consistently show all three funded positions, cash, exact UCITS identities, whole-share quantities, pricing dates, current weights, contribution, overlap and the reconciled equity curve. Dutch is primary; English is companion.

### Operational runbook

```text
manual dispatch corrected preview 20260717_005500
→ focused funded-aware regression tests
→ fresh UCITS pricing and macro refresh
→ normalized funded-aware state
→ Dutch and English HTML/PDF
→ strict funded-state consistency gate
→ complete page review
→ review manifest
→ no delivery without separate explicit authority
```
