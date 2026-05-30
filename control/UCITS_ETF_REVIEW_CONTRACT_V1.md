# UCITS ETF Review Contract V1

## Purpose

This contract defines the European / Dutch-client UCITS ETF review product.

The weekly ETF EU review decides which UCITS ETFs available to Dutch/EU investors deserve capital. It must not present U.S.-listed ETFs as investable Dutch/EU portfolio instruments.

## Decision framework

The EU model asks:

```text
Which UCITS ETFs available to Dutch/EU investors deserve capital this week?
```

Every funded candidate must pass:

1. UCITS status check.
2. PRIIPs / KID availability check.
3. ISIN-first identity check.
4. Exchange trading-line check.
5. Trading currency check, with EUR line preferred where practical.
6. Liquidity / spread / exchange suitability check where data is available.
7. TER / ongoing charges disclosure where data is available.
8. Replication method disclosure where data is available.
9. Distribution policy disclosure.
10. Currency exposure / hedging disclosure.

## Proxy rule

U.S.-listed ETFs may be used only as:

- research proxies;
- benchmark references;
- thematic comparators;
- historical signal inputs.

They may not be portfolio holdings in the EU model.

## Input/state contract

Canonical EU position identity is ISIN-first.

A funded EU position should contain:

```text
isin
fund_name
provider
ucits_status
priips_kid_status
domicile
base_currency
trading_currency
primary_exchange
exchange_ticker
provider_symbol
ter
replication_method
distribution_policy
hedged_unhedged
benchmark_index
```

## Output contract

The report must distinguish:

```text
UCITS ETF = investable instrument
U.S. ETF = research proxy / benchmark comparator only
```

The Dutch report is the primary client-facing output for the EU model.

## Operational contract

Production delivery remains blocked until EU validators pass.

Minimum validators:

- no U.S.-listed ETF as EU holding;
- every funded holding has an ISIN;
- every funded holding has UCITS status;
- every funded holding has PRIIPs/KID status;
- every funded holding has exchange ticker and trading currency;
- report includes UCITS/tradability disclosure.
