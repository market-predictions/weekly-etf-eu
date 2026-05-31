# Changelog — Phase 4 Euronext Search HTML Inspection

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: diagnostic-only inspection of Euronext search endpoint HTML.

## Current issue

The controlled endpoint evidence run showed that the selected Euronext search candidate returns HTML, not JSON. The next safe step was to inspect whether this HTML exposes stable product-card or link evidence, or whether it simply loops back to the search page.

## Change

Updated:

- pricing/build_euronext_endpoint_evidence.py

The endpoint evidence builder now inspects the fetched HTML for:

- canonical URL;
- whether the canonical URL equals the target search URL;
- identity-bearing hrefs;
- product-page links;
- search-page links;
- search-result and product-card term counts;
- whether the endpoint appears to loop back to a search page;
- a recommended next-step classification.

## Safety posture

This remains diagnostic-only. It does not extract a close price, validate completed session, create valuation authority, create funding authority, mutate portfolio state, generate PDF, send email, or create a delivery receipt.

## Next action

Queue the bootstrap workflow and inspect the new Euronext endpoint evidence artifact. If the search endpoint loops back without product-card links, stop spending effort on search endpoints and move to a typed product-page parser around custom.instrument and dynamic_quotes_display.
