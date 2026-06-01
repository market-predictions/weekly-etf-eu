# Changelog — Phase 4 Euronext Product-Page Evidence

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: diagnostic-only Euronext product-page evidence around custom.instrument and dynamic_quotes_display.

## Current issue

The Euronext search endpoint path proved to loop back to the search page and did not expose product-page links. The next safe route is the actual product page, where the close engine already observes typed Drupal settings around custom.instrument and dynamic_quotes_display.

## Change

Added:

- pricing/build_euronext_product_page_evidence.py
- tools/validate_euronext_product_page_evidence.py

Updated:

- .github/workflows/send-weekly-etf-eu-report.yml
- tools/build_etf_eu_shadow_validation_evidence.py
- tools/validate_etf_eu_shadow_validation_evidence.py

## Behavior

The workflow now builds a separate product-page evidence artifact from the existing close-observation diagnostics. The artifact captures custom.instrument identity evidence, dynamic_quotes_display evidence, the decision to stop the search-endpoint path, and the required promotion blockers.

Expected output pattern:

- output/pricing/euronext_product_page_evidence_YYYYMMDD_HHMMSS.json

## Safety posture

This artifact is evidence-only. It does not fetch a quote response, extract a close value, validate completed session, create valuation authority, create funding authority, mutate portfolio state, generate PDF, send email, or create a delivery receipt.

## Next action

Queue the bootstrap workflow and inspect the product-page evidence artifact. If custom.instrument and dynamic_quotes_display are stable, the next implementation step is a controlled product-page quote-response fetcher with no valuation promotion.
