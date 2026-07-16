# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-16

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Operating mode

```text
operating_mode=routine_production_with_active_model_portfolio
production_renderer=client_grade_v2_funded_aware
client_grade_v2_promoted=true
routine_production_ready=true
capital_activation_policy=control/ETF_EU_CAPITAL_ACTIVATION_POLICY_V1.md
selected_next_action=OBTAIN_FRESH_EXACT_LINE_PRICING_AND_BROKER_PERMISSION_THEN_REVIEW_VWCE_ACTIVATION
```

## Latest completed production delivery cycle

```text
work_package_id=ETF-EU-RUN260712-FIX2B_CORRECTED_RESEND_RECEIPT_CLOSEOUT
status=corrected_resend_receipt_confirmed_and_closed
report_date=2026-07-12
report_suffix=260712
github_workflow_run_id=29428021408
correction_transport_success=true
receipt_confirmed=true
expected_attachment_set_seen=true
attachment_count_seen=4
production_delivery_cycle_closed=true
additional_resend_required=false
```

This remains the latest email-delivery closeout. CAP01 and the subsequent routine allocation review performed no transport and sent no email.

## CAP01 — first guarded model capital activation

```text
work_package_id=ETF-EU-CAP01
run_id=20260716_012900
report_date=2026-07-16
status=model_capital_activated_report_generated_and_visually_reviewed
model_portfolio_only=true
real_broker_execution=false
personal_investment_advice=false
```

### Active portfolio state

```text
starting_capital_eur=100000.00
nav_eur=100000.00
cash_eur=92900.00
invested_market_value_eur=7100.00
position_count=1
```

### Funded model position

```text
isin=IE00B5BMR087
exchange_ticker=SXR8
exchange=Xetra
trading_currency=EUR
shares=10
model_entry_price_eur=710.00
latest_validated_exact_line_price_eur=710.00
latest_validated_price_date=2026-07-14
market_value_eur=7100.00
current_weight_pct=7.10
phase_target_weight_pct=7.50
strategic_target_weight_pct=15.00
```

## Routine allocation review — 20260716_092600

```text
artifact=output/runtime/etf_eu_routine_allocation_review_20260716_092600.json
validation=output/quality/etf_eu_routine_allocation_review_validation_20260716_092600.json
status=review_complete_no_model_mutation
portfolio_action=hold_sxr8_and_retain_cash
trade_intent_count=0
portfolio_mutation=false
second_tranche_authorized=false
```

### SXR8 result

```text
action=hold
review_price_eur=710.00
price_date=2026-07-14
unrealized_pnl_eur=0.00
unrealized_pnl_pct=0.00
portfolio_contribution_eur=0.00
role_validity=pass
relative_strength_status=insufficient_post_entry_window
```

A fresher completed exact-line Xetra close was not obtained through the available connected data path. The model therefore retained the latest validated exact-line close rather than inventing or substituting a price. No automatic second tranche is allowed.

## Candidate verification results

### VWCE — global core

```text
isin=IE00BK5BQT80
fund_identity=verified
ucits_status=confirmed
priips_kid_status=available
xetra_line=verified
exchange_ticker=VWCE
bloomberg_ticker=VWCE_GY
reuters_ric=VWCE.DE
trading_currency=EUR
allocation_status=verified_line_not_yet_fundable
```

Remaining blockers:

```text
fresh_completed_xetra_close_not_obtained
broker_account_product_permission_not_verified
separate_allocation_decision_required
```

The first-tranche overlap review is complete. A 25% VWCE sleeve would contain material embedded U.S. equity exposure alongside the direct SXR8 overweight, but the combined exposure remains within the current strategic design. This does not authorize funding.

### Aggregate bonds — EUNA / AGGH identity repair

```text
isin=IE00BDBRDM35
share_class=EUR_Hedged_Accumulating
ucits_status=confirmed
issuer_exchange_ticker=AGGH
bloomberg_identifier=EUNA
reuters_ric=EUNA.DE
pricing_symbol=EUNA.DE
identity_status=repaired
allocation_status=identity_repaired_not_yet_fundable
```

The incorrect LSE GBP Hedged Distributing mapping using ISIN `IE00BDBRDM35` has been removed. That ISIN identifies the EUR Hedged Accumulating share class. Broker-level execution-symbol confirmation and a fresh completed Xetra close remain required.

## Current evidence

```text
config/ucits_symbol_registry.yml
config/ucits_close_price_validation_basket.yml
output/instrument_verification/etf_eu_instrument_verification_20260716_092600.json
output/runtime/etf_eu_routine_allocation_review_20260716_092600.json
output/quality/etf_eu_routine_allocation_review_validation_20260716_092600.json
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_recommendation_scorecard.csv
```

## Strategic target policy

```text
global_core_VWCE=50.0%
us_equity_overweight_SXR8=15.0%
aggregate_bonds_EUNA=15.0%
nasdaq_satellite_SXRV=7.5%
semiconductor_satellite=5.0%
strategic_cash_reserve=7.5%
first_tranche_fraction=50.0%
blocked_capacity_policy=retain_as_cash
```

## Routine report architecture

```text
fresh UCITS pricing
+ active EU portfolio state
+ refreshed valuation history
+ current donor macro context adapted for EU use
+ UCITS registry
→ normalized ETF EU report state
→ funded-aware Dutch investor brief + analyst appendix
→ funded-aware English investor brief + analyst appendix
→ strict client-grade v2 validation
→ complete page review
→ guarded delivery and receipt layers only when explicitly authorized
```

Primary funded-aware production files:

```text
tools/build_etf_eu_routine_report_package_v2.py
runtime/build_etf_eu_client_grade_report_state.py
runtime/render_etf_eu_client_grade_v2_funded.py
runtime/polish_etf_eu_client_grade_html.py
runtime/build_etf_eu_allocation_decision.py
runtime/apply_etf_eu_guarded_capital_activation.py
tools/validate_etf_eu_allocation_decision.py
tools/validate_etf_eu_guarded_capital_activation.py
```

## Standing authority boundaries

```text
canonical_identity=isin_plus_exact_trading_line
us_etfs_research_only=true
model_portfolio_only=true
real_broker_execution=false
valuation_grade=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
```

## Current note

The routine review is closed with a clean hold and no model mutation. The next material action is not another architecture package. It is to obtain a fresh completed exact-line price and broker-account product permission evidence for VWCE, confirm the Xetra execution-symbol mapping for the aggregate-bond line, then run a new allocation review. Until those gates pass, SXR8 remains at 10 shares and blocked target capacity remains cash.
