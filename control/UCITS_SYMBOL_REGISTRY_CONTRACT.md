# UCITS Symbol Registry Contract

## Purpose

The EU ETF model is ISIN-first. Ticker symbols identify trading lines, not the canonical fund identity.

## Registry layers

The registry separates:

1. fund or share-class identity;
2. exchange trading line;
3. provider pricing symbol;
4. U.S. research proxy;
5. benchmark index.

## Minimum fields

```yaml
- isin: TBD
  fund_name: TBD
  provider: TBD
  ucits_status: pending_verification
  priips_kid_status: pending_verification
  domicile: TBD
  base_currency: TBD
  distribution_policy: TBD
  replication_method: TBD
  benchmark_index: TBD
  trading_lines:
    - exchange: TBD
      exchange_ticker: TBD
      trading_currency: EUR
      provider_symbol: TBD
      pricing_source_priority: []
  research_proxies:
    - us_proxy: TBD
      purpose: benchmark_reference_only
```

## Authority rule

A U.S. proxy ticker must not be written into `positions[]` as an EU holding.

A UCITS candidate can become fundable only after ISIN, exchange line, UCITS status and KID status are verified.
