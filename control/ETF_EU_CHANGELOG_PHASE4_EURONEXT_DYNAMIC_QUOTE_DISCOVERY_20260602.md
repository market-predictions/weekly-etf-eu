# Changelog — Phase 4 Euronext Dynamic Quote Response Discovery

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: diagnostic-only discovery for Euronext dynamic_quotes_display response behavior.

## Current issue

Product-page evidence confirmed that custom.instrument is usable for identity design and dynamic_quotes_display is present with a timer configuration. The next safe step is to discover whether the product page explicitly exposes the response endpoint used by dynamic_quotes_display.

## Change

Added:

- pricing/build_euronext_dynamic_quote_response_discovery.py
- tools/validate_euronext_dynamic_quote_response_discovery.py

Updated:

- .github/workflows/send-weekly-etf-eu-report.yml
- tools/build_etf_eu_shadow_validation_evidence.py
- tools/validate_etf_eu_shadow_validation_evidence.py

## Behavior

The new builder fetches only the official product page from the product-page evidence artifact, inspects Drupal settings, script src values and inline contexts, and samples at most one explicitly discovered response candidate if one is present in the page or settings.

The artifact answers:

- which endpoint or response appears to be triggered by dynamic_quotes_display;
- whether any sampled response looks structured;
- whether verified product identity appears preserved.

Expected output pattern:

- output/pricing/euronext_dynamic_quote_response_discovery_YYYYMMDD_HHMMSS.json

## Safety posture

This remains diagnostic-only. It does not extract a close value, validate completed session, create valuation authority, create funding authority, mutate portfolio state, generate PDF, send email, or create a delivery receipt.

## Next action

Queue the bootstrap workflow and inspect the discovery artifact. If no explicit response endpoint is exposed by the page/settings, stop the dynamic_quotes_display path and choose an alternative official-source strategy.
