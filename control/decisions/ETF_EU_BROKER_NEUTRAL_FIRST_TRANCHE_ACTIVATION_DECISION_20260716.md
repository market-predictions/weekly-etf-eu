# ETF EU Broker-Neutral First-Tranche Activation Decision

Date: 2026-07-16  
Repository: `market-predictions/weekly-etf-eu`  
Run id: `20260716_205500`  
Status: accepted for guarded repository-model activation

## Current issue

The broker-neutral allocation review has obtained usable completed-close observations and passed the active-portfolio, whole-share, cash-policy and authority validations for the verified Xetra lines SXR8, VWCE and EUNA.

The review produced two first-tranche model trade intents while retaining the existing SXR8 position without a second tranche.

## User authority

The user explicitly instructed the system to continue beyond the immediate operational step where no further user input is required.

That instruction is accepted only for the repository model portfolio and its deterministic evidence/state updates.

It does not authorize:

```text
real broker order
broker API execution
email delivery
production report delivery
personal investment advice
```

## Decision framework

The active model portfolio is revalued first:

```text
SXR8 shares=10
SXR8 completed close=EUR 711.66
SXR8 market value=EUR 7,116.60
cash before activation=EUR 92,900.00
revalued NAV=EUR 100,016.60
SXR8 action=hold
second tranche authorized=false
```

The following first-tranche additions are authorized:

```text
VWCE
isin=IE00BK5BQT80
venue=Xetra
shares=151
model price=EUR 165.32
model trade value=EUR 24,963.32
phase target weight=25.0%

EUNA
isin=IE00BDBRDM35
venue=Xetra
shares=1526
model price=EUR 4.913
cent-rounded model trade value=EUR 7,497.24
phase target weight=7.5%
```

Post-activation target state:

```text
cash=EUR 60,439.44
invested market value=EUR 39,577.16
NAV=EUR 100,016.60
position count=3
```

## Input/state contract

Authority inputs:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
config/etf_eu_target_allocation.yml
config/ucits_symbol_registry.yml
output/pricing/etf_eu_exact_line_review_pricing_20260716_205500.json
output/runtime/etf_eu_broker_neutral_allocation_review_20260716_205500.json
output/quality/etf_eu_broker_neutral_allocation_review_validation_20260716_205500.json
```

Canonical identity remains ISIN plus exact share class, venue, exchange trading line and currency. Broker/account symbols do not control model investability.

## Output contract

The guarded activation must write:

```text
updated output/etf_eu_portfolio_state.json
idempotent rows in output/etf_eu_trade_ledger.csv
updated output/etf_eu_valuation_history.csv
run-scoped activation result
run-scoped activation validation
run-scoped closeout manifest
```

Cash, invested value and NAV must reconcile to euro cents.

## Operational runbook

```text
validated broker-neutral review
→ explicit model confirmation
→ revalue incumbent SXR8
→ add VWCE and EUNA whole-share first tranches
→ reconcile cash and NAV
→ append idempotent trade ledger rows
→ refresh valuation history
→ validate official state
→ update CURRENT_STATE and NEXT_ACTIONS
```

## Authority boundary

```text
model_portfolio_only=true
portfolio_mutation=true
real_broker_execution=false
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
production_delivery=false
email_send=false
second_sxr8_tranche_authorized=false
```

The public completed-close observations remain non-authoritative for real-money execution. They are accepted only as transparent model-portfolio price bases under the existing policy.
