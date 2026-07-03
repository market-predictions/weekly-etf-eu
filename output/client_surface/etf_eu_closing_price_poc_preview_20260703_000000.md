# ETF EU Closing Price POC

## What this proves

This proof-of-concept attempts to connect one ISIN-first EU UCITS registry line to a provider close: **SXR8.DE / IE00B5BMR087**.

The system has the right registry link for a first attempt:

```text
isin=IE00B5BMR087
fund_name=iShares Core S&P 500 UCITS ETF USD (Acc)
exchange=Xetra
exchange_ticker=SXR8
trading_currency=EUR
pricing_symbol=SXR8.DE
```

## Closing price result

| ISIN | Fund | Trading line | Currency | Latest close date | Latest close | Source | Status |
|---|---|---|---|---:|---:|---|---|
| IE00B5BMR087 | iShares Core S&P 500 UCITS ETF USD (Acc) | SXR8.DE | EUR | — | — | yahoo_chart_v8_attempted | failed |

## What this does not prove

This is a limited proof-of-concept, not valuation-grade pricing and not delivery-ready evidence.

The current ChatGPT execution environment could not resolve the provider endpoint, and the available web finance/search tools did not return a usable SXR8.DE quote. No fake price was inserted, and no U.S. proxy price was used.

This does not create a funded holding, portfolio valuation, recommendation change, client-grade claim, or delivery-preflight authority.

## Next step

Repair provider access or symbol mapping until one real SXR8.DE closing-price POC succeeds.
