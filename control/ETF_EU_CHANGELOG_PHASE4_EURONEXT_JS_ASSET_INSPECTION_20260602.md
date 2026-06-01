# Changelog — Phase 4 Euronext JS Asset Inspection

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: diagnostic-only inspection of Euronext optimized JavaScript assets.

## Current issue

Dynamic quote response discovery confirmed that dynamic_quotes_display is present, but the product-page settings only expose a timer and no explicit usable quote response endpoint. The discovery artifact listed optimized JavaScript assets that may contain the dynamic quote behavior.

## Change

Added:

- pricing/build_euronext_js_asset_inspection.py
- tools/validate_euronext_js_asset_inspection.py

Updated:

- .github/workflows/send-weekly-etf-eu-report.yml
- tools/build_etf_eu_shadow_validation_evidence.py
- tools/validate_etf_eu_shadow_validation_evidence.py

## Behavior

The workflow now fetches the JavaScript assets listed by dynamic quote response discovery and records bounded diagnostics:

- term counts for dynamic quote, quote, close, price and related strings;
- bounded context samples;
- quoted route-like candidates;
- whether meaningful quote or price route candidates exist.

Expected output pattern:

- output/pricing/euronext_js_asset_inspection_YYYYMMDD_HHMMSS.json

## Safety posture

This remains diagnostic-only. It does not sample a discovered route, extract a close value, validate completed session, create valuation authority, create funding authority, mutate portfolio state, generate PDF, send email, or create a delivery receipt.

## Yahoo Finance note

Yahoo/yfinance remains non-authoritative connectivity only in the EU repo. It may have historical closes for some UCITS trading lines, but it requires per-line proof of ticker suffix, currency, close date and source lineage before any valuation use.

## Next action

Queue the bootstrap workflow and inspect the JS asset inspection artifact. If a stable official route candidate appears, the next patch can add a controlled route evidence fetcher with no valuation promotion.
