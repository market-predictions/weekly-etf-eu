# Changelog — Phase 4 Euronext Endpoint Probe Diagnostics

Date: 2026-06-01
Repository: `market-predictions/weekly-etf-eu`
Scope: Euronext adapter endpoint research inside the generic UCITS close-price engine.

## Current issue

The Euronext adapter had observed `baseUrlSearchQuote`, `dynamic_quotes_display`, `product_data` and `currentPath` hints, but it did not yet test whether the search endpoint can return product-specific structured data.

## Change

Updated:

```text
pricing/close_engine/adapters/euronext.py
```

The adapter now performs limited non-authoritative endpoint probes derived from the observed `baseUrlSearchQuote` hint and the verified trading-line identity:

- product code;
- ISIN;
- exchange ticker.

The probes record only diagnostic metadata:

- HTTP status;
- content type;
- whether the sampled body looks like JSON;
- whether it contains ISIN, exchange ticker, trading currency or quote-related terms;
- a short body sample.

## Authority impact

No price parsing was added.

The adapter still emits:

```text
candidate_close=null
candidate_date=null
candidate_currency=null
completed_session=false
valuation_authority=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
```

## Next action

Queue the bootstrap workflow and inspect the persisted close-observation artifact. If one of the probes reliably returns product-specific structured data, the next step is to turn that endpoint into a typed diagnostic fetcher before any valuation-grade promotion logic exists.
