# Weekly ETF EU Review OS — Next Actions

Current priority:

```text
OBTAIN_FRESH_EXACT_LINE_PRICING_AND_BROKER_PERMISSION_THEN_REVIEW_VWCE_ACTIVATION
```

## Current production and portfolio status

```text
client_grade_v2_promoted=true
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
cap01_completed=true
routine_review_20260716_092600_completed=true
model_portfolio_active=true
position_count=1
cash_eur=92900.00
invested_market_value_eur=7100.00
nav_eur=100000.00
```

The cash-only bootstrap lane and CAP01 are closed. Do not recreate them. Ordinary repricing, position review, candidate verification and allocation decisions remain routine operations.

## Completed in routine review 20260716_092600

```text
SXR8_repriced_to_latest_available_validated_exact_line_close=true
SXR8_contribution_calculated=true
SXR8_action=hold
second_tranche_authorized=false
VWCE_fund_identity_verified=true
VWCE_Xetra_line_verified=true
VWCE_KID_verified=true
EUNA_AGGH_identity_inconsistency_repaired=true
new_allocation_decision_completed=true
portfolio_mutation=false
trade_intent_count=0
```

Canonical review artifacts:

```text
output/instrument_verification/etf_eu_instrument_verification_20260716_092600.json
output/runtime/etf_eu_routine_allocation_review_20260716_092600.json
output/quality/etf_eu_routine_allocation_review_validation_20260716_092600.json
```

## Current funded model position

```text
isin=IE00B5BMR087
exchange_ticker=SXR8
exchange=Xetra
trading_currency=EUR
shares=10
model_entry_price_eur=710.00
latest_validated_price_eur=710.00
latest_validated_price_date=2026-07-14
current_model_weight_pct=7.10
phase_target_weight_pct=7.50
strategic_target_weight_pct=15.00
current_action=hold
```

The contribution since entry remains €0.00 based on the latest validated exact-line close. A fresher completed Xetra close was not obtained through the available connected data path, so no substitute or inferred price was used.

## Immediate next evidence tasks

### 1. Fresh exact-line pricing

Obtain a new completed-close artifact for:

```text
SXR8.DE
VWCE.DE
EUNA.DE
```

Requirements:

- exact ISIN and Xetra-line reconciliation;
- completed close, not intraday indicative pricing;
- explicit close date and observed timestamp;
- source provenance;
- no silent substitution of issuer NAV for exchange close.

### 2. Broker-account product permission

For VWCE, verify:

```text
broker=Interactive Brokers or configured production broker
contract_identity=IE00BK5BQT80 + Xetra + VWCE
trading_currency=EUR
product_permission_available=true|false
account_region_eligible=true|false
```

Do not infer account permission merely because the venue is generally supported.

### 3. Aggregate-bond execution-symbol confirmation

The share-class identity is repaired:

```text
isin=IE00BDBRDM35
share_class=EUR Hedged Accumulating
issuer_exchange_ticker=AGGH
bloomberg_identifier=EUNA
reuters_ric=EUNA.DE
```

Confirm which identifier the configured broker requires for the Xetra order contract. Do not reintroduce the removed GBP Hedged Distributing mapping.

## Next allocation review

Only after the above evidence exists, create a new run-scoped allocation decision that determines:

1. whether SXR8 remains hold, add, reduce or exit;
2. whether a second SXR8 tranche is justified after a sufficient confirming window;
3. whether VWCE can receive the 25% first-tranche global-core allocation;
4. whether aggregate bonds can receive their 7.5% first tranche;
5. whole-share sizing, residual cash and overlap consequences;
6. explicit `trade_intents[]` or an explicit no-trade result.

No automatic second tranche or new position is authorized.

## Current candidate status

### VWCE — global core

```text
strategic_target_weight_pct=50.0
first_tranche_target_weight_pct=25.0
fund_identity=verified
xetra_line=verified
kid=available
status=verified_line_not_yet_fundable
```

Remaining blockers:

```text
fresh_completed_xetra_close_not_obtained
broker_account_product_permission_not_verified
separate_new_allocation_decision_required
```

### Aggregate bonds

```text
strategic_target_weight_pct=15.0
first_tranche_target_weight_pct=7.5
identity_status=repaired
status=not_yet_fundable
```

Remaining blockers:

```text
broker_execution_symbol_mapping_not_verified
fresh_completed_xetra_close_not_obtained
separate_new_allocation_decision_required
```

### Satellites

```text
SXRV_target=7.5%
semiconductor_target=5.0%
current_status=blocked
```

Keep these as satellites. Require exact-line verification, fresh pricing and concentration review. The semiconductor line also requires an approved EUR/FX execution policy.

## Cash policy

```text
minimum_strategic_cash_reserve_pct=7.5
blocked_capacity_policy=retain_as_cash
blocked_capacity_reallocation=false
current_cash_weight_pct=92.9
```

The high cash weight is temporary blocked capacity, not a permanent bearish call.

## Equity surface

```text
portfolio_position_count=1
current_equity_surface=active_equity_curve
latest_nav_eur=100000.00
```

The equity curve must reconcile to `output/etf_eu_valuation_history.csv` and current portfolio state. A flat contribution at the retained close must be described truthfully.

## Closed identities

Do not reuse:

```text
work_package_id=ETF-EU-CAP01
run_id=20260716_012900
activation_id=ETF-EU-CAP01-20260716_012900
review_run_id=20260716_092600
report_suffix=260716
trade_id=model-eu-2026-07-16-20260716_012900-02-SXR8-BUY
```

## Development rule

Repair concrete defects directly in the funded-aware production path. Create a new architecture package only for a material capability change. The next work is evidence acquisition and a routine allocation review, not another architecture cycle.
