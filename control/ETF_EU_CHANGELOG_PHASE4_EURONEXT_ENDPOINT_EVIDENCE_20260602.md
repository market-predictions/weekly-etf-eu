# Changelog — Phase 4 Euronext Endpoint Evidence

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: controlled single-candidate Euronext endpoint evidence.

## Current issue

The previous run produced quote endpoint candidates from the verified Euronext custom instrument identity. The next safe step was to fetch exactly one candidate URL as evidence without parsing or promoting a close price.

## Change

Added:

- pricing/build_euronext_endpoint_evidence.py
- tools/validate_euronext_endpoint_evidence.py

Updated:

- .github/workflows/send-weekly-etf-eu-report.yml
- tools/build_etf_eu_shadow_validation_evidence.py
- tools/validate_etf_eu_shadow_validation_evidence.py

## Behavior

The workflow now reads the close-observation artifact, selects the settings_search_product_data candidate URL, fetches only that URL, records a bounded response sample and identity/quote-term signals, validates that the artifact remains diagnostic-only, and commits the artifact under output/pricing.

Expected output pattern:

- output/pricing/euronext_endpoint_evidence_YYYYMMDD_HHMMSS.json

## Safety posture

The endpoint evidence artifact is not valuation-grade. It cannot create candidate close, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation, email delivery, or production delivery.

## Next action

Queue the bootstrap workflow and inspect the endpoint evidence artifact. If the sampled response shows structured identity/quote signals, the next patch can design a typed response parser. That parser must still be blocked from valuation authority until close, date, currency, completed session, lineage, and staleness are separately validated.
