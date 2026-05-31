# Changelog — Phase 4 Euronext Product-Link Probe Diagnostics

Date: 2026-06-01
Repository: `market-predictions/weekly-etf-eu`
Scope: Euronext adapter product-link diagnostics inside the generic UCITS close-price engine.

## Current issue

The first Euronext endpoint probes showed that search-path URLs return HTML rather than JSON. Those pages still expose useful canonical and product-page signals, but the adapter did not yet extract those signals in a structured way.

The first probe also used a weak currency containment check. A naive `EUR` substring can create false positives inside words such as `Euronext`.

## Change

Updated:

```text
pricing/close_engine/adapters/euronext.py
```

The adapter now records additional non-authoritative diagnostics from Euronext search probe responses:

- canonical URL, when present;
- whether the canonical URL matches the expected ISIN pattern;
- product-link candidate count;
- product-link candidate list;
- resolved product URL candidates aggregated across probes;
- stricter whole-token currency matching.

## Authority impact

No close-price extraction was added.

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

Queue the bootstrap workflow and inspect the persisted close-observation artifact. If the product-link diagnostics consistently resolve the expected product URL, the next implementation step should be a typed Euronext product-page diagnostic fetcher, still without valuation-grade promotion.
