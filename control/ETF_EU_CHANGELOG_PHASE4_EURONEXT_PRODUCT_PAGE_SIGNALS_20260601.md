# Changelog — Phase 4 Euronext Product-Page Signal Diagnostics

Date: 2026-06-01
Repository: `market-predictions/weekly-etf-eu`
Scope: typed Euronext product-page signal diagnostics inside the generic UCITS close-price engine.

## Current issue

The previous Euronext probe work confirmed that search-path probes can resolve the expected Euronext product page, but the adapter still needed typed diagnostics for the product page itself.

Specifically, the product page contains signals such as:

- `dynamic_quotes_display`
- `product_data`
- `ajax`
- `ajaxPageState`
- `ajaxTrustedUrl`
- `baseUrlSearchQuote`
- Drupal settings JSON

These are likely closer to the reusable quote endpoint than generic page text, but they must be inspected conservatively before any close-price parser or valuation-grade promotion exists.

## Change

Updated:

```text
pricing/close_engine/adapters/euronext.py
```

The adapter now records a `product_page_signal_diagnostics` object containing:

- signal terms present;
- signal-term counts;
- bounded signal context samples;
- endpoint candidate samples;
- Drupal settings parse status;
- Drupal settings top-level keys;
- AJAX keys;
- AJAX page-state keys;
- signal key paths;
- endpoint-like values from parsed settings;
- product identity token presence for ISIN, exchange ticker and currency token.

## Authority impact

No price extraction was added.

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

The diagnostics are explicitly evidence-only and remain blocked from valuation authority.

## Next action

Queue the bootstrap workflow and inspect the persisted close-observation artifact. If the Drupal settings diagnostics expose a stable quote endpoint, the next step should be a typed endpoint fetcher that records raw source-lineage evidence only. A separate promotion layer must still validate source, close, date, currency, completed session, source lineage and staleness before any valuation authority exists.
