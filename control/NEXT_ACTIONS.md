# Weekly ETF EU Review OS — Next Actions

Current priority:

```text
OBTAIN_FRESH_EXACT_LINE_PRICING_THEN_RUN_BROKER_NEUTRAL_VWCE_EUNA_ALLOCATION_REVIEW
```

## Current production and portfolio status

```text
client_grade_v2_promoted=true
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
cap01_completed=true
routine_review_20260716_092600_completed=true
broker_neutral_model_authority_corrected=true
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

Canonical historical review artifacts:

```text
output/instrument_verification/etf_eu_instrument_verification_20260716_092600.json
output/runtime/etf_eu_routine_allocation_review_20260716_092600.json
output/quality/etf_eu_routine_allocation_review_validation_20260716_092600.json
```

These historical artifacts remain unchanged. Their broker-specific blocker wording is superseded prospectively by:

```text
control/decisions/ETF_EU_BROKER_NEUTRAL_MODEL_INVESTABILITY_DECISION_20260716.md
control/ETF_EU_CAPITAL_ACTIVATION_POLICY_V1.md
control/UCITS_INVESTABILITY_RULES.md
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

## Broker-neutral authority rule

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

The Weekly ETF EU Report and model portfolio must not depend on Interactive Brokers or another named broker. Account permission, broker contract IDs, local symbols and routing are checked only in an optional real-execution adapter after the model allocation decision.

## Immediate next evidence tasks

### 1. Fresh exact-line pricing

Obtain a new completed-close artifact for:

```text
SXR8.DE
VWCE.DE
canonical aggregate-bond Xetra line for IE00BDBRDM35
```

Requirements:

- exact ISIN, share class and Xetra-line reconciliation;
- completed close, not intraday indicative pricing;
- explicit close date and observed timestamp;
- source provenance;
- no silent substitution of issuer NAV for exchange close;
- no broker-specific permission requirement.

### 2. Broker-neutral aggregate-bond alias reconciliation

Canonical identity:

```text
isin=IE00BDBRDM35
share_class=EUR Hedged Accumulating
venue=Xetra
trading_currency=EUR
```

Known aliases:

```text
issuer_exchange_ticker=AGGH
bloomberg_identifier=EUNA
reuters_ric=EUNA.DE
pricing_symbol=EUNA.DE
```

Confirm in `config/ucits_symbol_registry.yml` which exact exchange trading line is canonical for the model. Retain all other symbols as typed aliases. Do not introduce a broker contract symbol as model authority and do not reintroduce the removed GBP Hedged Distributing mapping.

### 3. Optional real-execution evidence

Only when a real order is contemplated, verify through the chosen broker/account:

```text
contract lookup
product permission
account eligibility
order routing
cost and spread
order preview
```

This optional lane does not block the general report or model allocation.

## Next allocation review

After fresh pricing and canonical line reconciliation exist, create a new run-scoped broker-neutral allocation decision that determines:

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
status=verified_line_waiting_for_fresh_price_and_new_decision
```

Remaining model blockers:

```text
fresh_completed_xetra_close_not_obtained
separate_new_allocation_decision_required
```

### Aggregate bonds

```text
strategic_target_weight_pct=15.0
first_tranche_target_weight_pct=7.5
identity_status=repaired
status=waiting_for_broker_neutral_line_reconciliation_and_fresh_price
```

Remaining model blockers:

```text
canonical_xetra_exchange_line_alias_reconciliation_required
fresh_completed_xetra_close_not_obtained
separate_new_allocation_decision_required
```

### Satellites

```text
SXRV_target=7.5%
semiconductor_target=5.0%
current_status=blocked
```

Keep these as satellites. Require exact-line verification, fresh pricing and concentration review. The semiconductor line also requires an approved EUR/FX model-execution policy. A later real order may require broker-specific checks, but those are not model-investability gates.

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

Repair concrete defects directly in the funded-aware production path. Create a new architecture package only for a material capability change. The next work is fresh pricing, broker-neutral registry reconciliation and a routine allocation review, not another architecture cycle.
