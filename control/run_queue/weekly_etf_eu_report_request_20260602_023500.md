# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-02T00:35:00Z
mode: phase4_euronext_product_page_evidence_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding diagnostic-only Euronext product-page evidence around custom.instrument and dynamic_quotes_display.

## Expected behavior

- run all existing EU bootstrap validations;
- build and validate Euronext endpoint evidence;
- build and validate Euronext product-page evidence;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact including product-page evidence;
- keep quote response fetches, candidate closes, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
