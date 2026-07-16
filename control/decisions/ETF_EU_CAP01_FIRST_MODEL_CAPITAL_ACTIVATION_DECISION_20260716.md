# ETF EU CAP01 — First model capital activation decision

## Decision date

2026-07-16

## Decision

Activate the first Weekly ETF EU **repository model-portfolio** position through the verified Xetra EUR trading line of the iShares Core S&P 500 UCITS ETF.

```text
isin=IE00B5BMR087
exchange_ticker=SXR8
exchange=Xetra
trading_currency=EUR
whole_shares=10
model_entry_price_eur=710.00
model_market_value_eur=7100.00
model_weight_pct=7.10
phase_target_weight_pct=7.50
```

No real brokerage order was placed.

## Decision framework

The adopted allocation framework is core-satellite with strategic targets defined in `config/etf_eu_target_allocation.yml`.

The first activation phase uses 50% of each strategic sleeve target. A sleeve may receive capital only after its own exact instrument, trading-line, pricing, currency and policy gates pass.

Blocked sleeve capacity remains cash. It is not redistributed to another executable sleeve.

## Input/state authority

```text
portfolio_state=output/etf_eu_portfolio_state.json
trade_ledger=output/etf_eu_trade_ledger.csv
valuation_history=output/etf_eu_valuation_history.csv
allocation_policy=config/etf_eu_target_allocation.yml
pricing_evidence=output/pricing/ucits_close_price_validation_basket_results_20260716_012900.json
```

Canonical identity is ISIN plus exact trading line.

The model entry price uses the latest successful repository pricing evidence available in the session. Its explicit close date is 2026-07-14 and its quality remains `priced_non_authoritative`. It is valid only for the transparent repository model portfolio and is not a claim about a real execution price.

## Output contract

The activation decision and validations prove:

```text
whole_shares_only=true
nav_reconciliation_ok=true
cash_reconciliation_passed=true
ledger_persistence_passed=true
blocked_capacity_reallocated=false
model_portfolio_only=true
real_broker_execution=false
```

Post-activation state:

```text
nav_eur=100000.00
cash_eur=92900.00
invested_market_value_eur=7100.00
position_count=1
```

## Blocked strategic sleeves

The following targets remain unfunded:

- VWCE global core: exact trading-line verification pending;
- EUNA aggregate bonds: trading-line verification and share-class/ISIN repair pending;
- SXRV Nasdaq satellite: trading-line verification pending;
- semiconductor satellite: trading-line verification and EUR/FX execution policy pending.

## Operational consequence

The cash-only bootstrap period is closed. Routine Weekly ETF EU reports must now use the funded-aware client-grade v2 renderer and must review the SXR8 position every cycle.

No second tranche is automatic. Additional capital requires a fresh allocation decision using current completed-close pricing and current portfolio state.

## Evidence

```text
output/allocation/etf_eu_allocation_decision_20260716_012900.json
output/quality/etf_eu_allocation_decision_validation_20260716_012900.json
output/runtime/etf_eu_guarded_capital_activation_result_20260716_012900.json
output/quality/etf_eu_guarded_capital_activation_validation_20260716_012900.json
output/quality/etf_eu_routine_pdf_visual_review_20260716_012900.json
output/run_manifests/etf_eu_cap01_closeout_manifest_20260716_012900.json
```
