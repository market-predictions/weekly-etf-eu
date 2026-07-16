# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-07-16
repository=market-predictions/weekly-etf-eu
operating_mode=routine_production_with_three_position_active_model_portfolio
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
selected_next_action=GENERATE_AND_VISUALLY_REVIEW_FUNDED_AWARE_THREE_POSITION_ROUTINE_REPORT
```

## Latest completed delivery

```text
work_package_id=ETF-EU-RUN260712-FIX2B_CORRECTED_RESEND_RECEIPT_CLOSEOUT
report_date=2026-07-12
github_workflow_run_id=29428021408
receipt_confirmed=true
production_delivery_cycle_closed=true
```

This remains the latest email-delivery closeout. The 2026-07-16 allocation and activation cycle performed no transport and sent no email.

## Broker-neutral review and activation

```text
run_id=20260716_205500
status=model_activation_applied_validated_and_closed
review=output/runtime/etf_eu_broker_neutral_allocation_review_20260716_205500.json
review_validation=output/quality/etf_eu_broker_neutral_allocation_review_validation_20260716_205500.json
activation_result=output/runtime/etf_eu_broker_neutral_model_activation_result_20260716_205500.json
activation_validation=output/quality/etf_eu_broker_neutral_model_activation_validation_20260716_205500.json
closeout_manifest=output/run_manifests/etf_eu_broker_neutral_model_activation_manifest_20260716_205500.json
portfolio_mutation=true
real_broker_execution=false
production_delivery=false
github_actions_run_verified=false
```

The connector-authored queue did not produce a verifiable Actions run. The review and guarded model activation were executed and checked in-session; no workflow-success claim is made.

## Active model portfolio

```text
starting_capital_eur=100000.00
nav_eur=100016.60
cash_eur=60439.44
invested_market_value_eur=39577.16
cash_weight_pct=60.4294
position_count=3
```

Cash plus invested market value reconciles exactly to NAV at eurocent precision.

| Position | ISIN | Shares | Model price | Market value | Weight | Action |
|---|---|---:|---:|---:|---:|---|
| VWCE | IE00BK5BQT80 | 151 | €165.32 | €24,963.32 | 24.959177% | Buy |
| EUNA | IE00BDBRDM35 | 1,526 | €4.913 | €7,497.24 | 7.495996% | Buy |
| SXR8 | IE00B5BMR087 | 10 | €711.66 | €7,116.60 | 7.115419% | Hold |

VWCE is the global-core first tranche. EUNA is the EUR-hedged aggregate-bond first tranche. EUNA is the canonical repository Xetra ticker; AGGH is retained as issuer alias. SXR8 was revalued from €710.00 to €711.66, producing €16.60 unrealized model P&L. No second SXR8 tranche is authorized.

## Ledger and valuation authority

```text
trade_ledger=output/etf_eu_trade_ledger.csv
valuation_history=output/etf_eu_valuation_history.csv
new_trade_id_1=model-eu-2026-07-16-20260716_205500-01-VWCE-BUY
new_trade_id_2=model-eu-2026-07-16-20260716_205500-02-EUNA-BUY
latest_nav_eur=100016.60
since_inception_return_pct=0.016600
drawdown_pct=0.000000
```

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

Broker product permission, account eligibility, contract IDs, routing and order preview belong only to an optional real-execution adapter.

## Four-layer status

### Decision framework

Model investability requires verified UCITS/KID status, canonical identity, verified exchange line, fresh completed-close pricing, currency/product-policy gates, concentration review, whole-share sizing and cash reconciliation. No automatic later tranche or satellite activation is authorized.

### Input/state contract

```text
config/ucits_symbol_registry.yml
config/ucits_close_price_validation_basket.yml
config/etf_eu_target_allocation.yml
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
output/etf_eu_valuation_history.csv
output/pricing/etf_eu_exact_line_review_pricing_20260716_205500.json
```

Public closes remain model-only, non-valuation-grade evidence and are not real execution prices.

### Output contract

The next report must show three funded model positions, cash, quantities, exact UCITS lines, price dates, weights, contribution, equity curve and explicit model-only disclosures. Dutch is primary; English is companion.

### Operational runbook

```text
three-position portfolio state
+ valuation history
+ exact-line pricing
+ donor macro context adapted for EU
+ UCITS registry
→ funded-aware report state
→ Dutch and English client-grade v2 reports
→ strict validation
→ complete visual review
→ no delivery without explicit authority and receipt evidence
```

## Current note

The broker-neutral first-tranche activation is closed. The next work is routine funded-aware report generation and visual review, followed by monitoring of VWCE, EUNA and SXR8. No real order and no report delivery are authorized.
