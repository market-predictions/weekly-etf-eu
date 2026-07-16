# ETF EU Routine Position and Identifier Decision — 2026-07-16

Repository: `market-predictions/weekly-etf-eu`  
Run id: `20260716_092600`

## Decision framework

1. `SXR8` receives the canonical action `hold`.
2. No automatic second tranche is permitted after the initial capital activation.
3. A second tranche requires a fresh completed exact-line close, a sufficient confirming window, intact thesis/role evidence, concentration review and a new run-scoped allocation decision.
4. Verified but blocked target capacity remains cash and is not redistributed to another sleeve.

## Input and state contract

1. Current portfolio state remains the quantitative authority.
2. Exchange-close evidence and issuer NAV are separate evidence types; issuer NAV must not be substituted for an exact Xetra close.
3. Canonical UCITS identity is `ISIN + venue + exact line identifiers`, not ticker alone.
4. Broker account-level product permission is a separate gate from general venue availability.

## Instrument identity decisions

### VWCE

```text
isin=IE00BK5BQT80
venue=Xetra
exchange_ticker=VWCE
bloomberg_ticker=VWCE GY
reuters_ric=VWCE.DE
trading_currency=EUR
line_status=verified_ucits_trading_line
```

VWCE is verified at fund, KID and exact Xetra-line level. It remains unfunded until a fresh completed close and broker-account product permission are evidenced and a new allocation decision authorizes capital.

### Aggregate bonds

```text
isin=IE00BDBRDM35
share_class=EUR Hedged Accumulating
venue=Xetra
issuer_exchange_ticker=AGGH
bloomberg_identifier=EUNA
reuters_ric=EUNA.DE
```

The previous `AGGH.L / GBP Hedged Distributing` mapping with ISIN `IE00BDBRDM35` is invalid and removed. The ISIN identifies the EUR Hedged Accumulating share class. The configured broker must confirm which identifier resolves the Xetra order contract before funding.

## Output contract

The run-scoped review must expose:

```text
incumbent_reviews[]
candidate_reviews[]
action_code
reason_codes
trade_intents[]
second_tranche_authorized
portfolio_mutation
authority boundaries
```

The report and ledger may not infer a trade from prose. Only explicit `trade_intents[]` can support a later guarded mutation.

## Operational result

```text
SXR8_action=hold
SXR8_contribution_eur=0.00
trade_intent_count=0
portfolio_mutation=false
cash_eur=92900.00
invested_market_value_eur=7100.00
nav_eur=100000.00
production_delivery_authority=false
```

Canonical evidence:

```text
output/instrument_verification/etf_eu_instrument_verification_20260716_092600.json
output/runtime/etf_eu_routine_allocation_review_20260716_092600.json
output/quality/etf_eu_routine_allocation_review_validation_20260716_092600.json
```
