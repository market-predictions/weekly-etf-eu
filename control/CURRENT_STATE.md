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
selected_next_action=RUN_NEXT_ROUTINE_REPORT_AND_MONITOR_FIRST_POSITION
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

This remains the latest email-delivery closeout. CAP01 performed no transport and sent no email.

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

### Portfolio state

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
market_value_eur=7100.00
current_weight_pct=7.10
phase_target_weight_pct=7.50
strategic_target_weight_pct=15.00
```

Authority and execution facts:

```text
whole_shares_only=true
exact_isin_and_line_verified=true
blocked_capacity_reallocated=false
blocked_target_capacity_retained_as_cash=true
broker_order_placed=false
```

The model entry uses the latest successful repository pricing evidence available to the session. Its explicit close date is 2026-07-14. It remains `priced_non_authoritative` and is not represented as a real brokerage execution price.

## CAP01 validation evidence

```text
focused_tests_passed=true
allocation_decision_valid=true
whole_share_contract_passed=true
cash_reconciliation_passed=true
portfolio_reconciliation_passed=true
ledger_persistence_passed=true
model_only_authority_passed=true
strict_client_grade_v2_validation_passed=true
visual_review_passed=true
dutch_page_count=6
english_page_count=6
blocker_count=0
```

Canonical evidence:

```text
output/allocation/etf_eu_allocation_decision_20260716_012900.json
output/quality/etf_eu_allocation_decision_validation_20260716_012900.json
output/pricing/ucits_close_price_validation_basket_results_20260716_012900.json
output/runtime/etf_eu_guarded_capital_activation_result_20260716_012900.json
output/quality/etf_eu_guarded_capital_activation_validation_20260716_012900.json
output/quality/etf_eu_routine_pdf_visual_review_20260716_012900.json
output/run_manifests/etf_eu_cap01_closeout_manifest_20260716_012900.json
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
output/etf_eu_valuation_history.csv
```

The four generated HTML/PDF files were produced and visually reviewed in-session. Their hashes and sizes are recorded in the closeout manifest. Binary repository persistence was not available through the connected GitHub write surface in this session; no false GitHub-delivery claim is made.

## Strategic target policy

```text
global_core_VWCE=50.0%
us_equity_overweight_SXR8=15.0%
aggregate_bonds_EUNA=15.0%
nasdaq_satellite_SXRV=7.5%
semiconductor_satellite=5.0%
strategic_cash_reserve=7.5%
first_tranche_fraction=50.0%
```

Only SXR8 passed every CAP01 activation gate. VWCE, EUNA, SXRV and the semiconductor line remain blocked; their capacity remains cash.

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
→ existing guarded delivery and receipt layers when explicitly authorized
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
canonical_identity=isin_first_plus_exact_trading_line
us_etfs_research_only=true
model_portfolio_only=true
real_broker_execution=false
valuation_grade=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
```

## Current note

The cash-only bootstrap period is closed. The EU model portfolio now has one guarded UCITS position. No automatic second tranche is authorized. The next routine cycle must reprice the portfolio, review SXR8 contribution and relative strength, preserve blocked capacity as cash, and separately verify the preferred global-core and aggregate-bond trading lines before considering additional model capital.
