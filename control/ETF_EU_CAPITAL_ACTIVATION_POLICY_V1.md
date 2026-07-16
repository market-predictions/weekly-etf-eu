# ETF EU Capital Activation Policy V1

Date: 2026-07-16  
Repository: `market-predictions/weekly-etf-eu`

## Purpose

Convert a verified UCITS candidate into a deterministic **model-portfolio** allocation while preserving ISIN-first identity, whole-share execution, residual cash and explicit authority boundaries.

## Decision framework

The strategic core-satellite targets are defined in `config/etf_eu_target_allocation.yml`. Initial activation uses a 50% first tranche. Capacity belonging to blocked candidates remains cash and is never reassigned to another exposure merely because that exposure is executable.

A target is executable in the repository model only when all hard gates pass:

1. exact ISIN and trading-line ticker match;
2. instrument type is UCITS ETF;
3. UCITS trading line is verified;
4. current close is available and no older than three calendar days;
5. trading currency is within the CAP01 currency scope;
6. whole-share order fits available cash after the minimum cash reserve;
7. no unresolved product-policy blocker applies.

Broker-specific account permission, broker contract IDs and broker order-routing aliases are not model-allocation gates. They belong to a separate real-execution adapter and must be checked only before a real order is prepared or submitted.

## Input/state contract

Authority inputs:

- `output/etf_eu_portfolio_state.json` — current model portfolio quantity authority;
- `output/pricing/ucits_close_price_validation_basket_results_<run_id>.json` — current market-close observation;
- `config/etf_eu_target_allocation.yml` — strategic target and activation policy;
- `output/etf_eu_trade_ledger.csv` — idempotency and transaction history.

Yahoo/yfinance observations remain non-authoritative for real-money execution. CAP01 permits them only as a transparent model-portfolio close basis after the exact UCITS trading line is verified.

Canonical model identity is:

```text
ISIN
+ exact share class
+ exchange / venue
+ exchange trading line
+ trading currency
```

Issuer, market-data-vendor and broker aliases may be retained as mappings, but none replaces the canonical identity.

## Output contract

The allocation decision records, for every target:

- strategic and phase target weight;
- current and target whole shares;
- executable share delta;
- trade value and residual cash;
- eligibility, blockers and reason codes;
- exact ISIN, exchange line, currency and pricing date.

Blockers in a model-allocation decision must describe product, identity, pricing, currency, concentration, sizing or cash-policy conditions. A missing broker permission must not block the broker-neutral model portfolio.

Blocked target capacity remains visible and stays in cash.

## Operational runbook

```text
fresh current pricing
→ allocation dry run
→ strict allocation validation
→ explicit model-capital confirmation
→ idempotent portfolio-state and trade-ledger mutation
→ valuation-history refresh
→ client-grade v2 report generation
```

A separate optional real-execution lane may later perform:

```text
canonical model trade intent
→ broker adapter
→ broker contract lookup
→ account permission check
→ order preview
→ explicit real-order authority
```

Failure in that optional lane does not retroactively invalidate the model decision; it prevents only real execution through that broker/account.

## Authority boundary

```text
model_portfolio_only=true
real_broker_execution=false
personal_investment_advice=false
whole_shares_only=true
blocked_capacity_reallocated=false
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

No real brokerage order is placed. This policy changes only the repository's model portfolio.
