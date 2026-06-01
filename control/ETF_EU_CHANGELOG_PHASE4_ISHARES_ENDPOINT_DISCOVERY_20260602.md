# Changelog — Phase 4 iShares Reference Endpoint Discovery

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Diagnostic endpoint discovery for BlackRock/iShares issuer reference evidence.

## Current issue

The generic iShares product HTML page fetched successfully but did not expose sufficient product identity or reference-price/NAV evidence in the initial sampled shell. The next safe step is to discover stable issuer data endpoints, static JSON, factsheet links, performance/NAV endpoints, or product-data URLs without extracting valuation data.

## Change

Added:

- pricing/build_ishares_reference_endpoint_discovery.py
- tools/validate_ishares_reference_endpoint_discovery.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now builds a diagnostic iShares endpoint discovery artifact. The artifact inspects the configured issuer product page for bounded candidate links and route-like strings related to:

- API or JSON endpoints;
- factsheet/document downloads;
- NAV, price, performance or chart routes;
- product or fund data routes.

Expected output pattern:

- output/pricing/ishares_reference_endpoint_discovery_YYYYMMDD_HHMMSS.json

## Safety posture

This is discovery-only. It does not fetch discovered endpoint candidates, extract NAV/reference price, create cross-source pass, create valuation authority, create funding authority, mutate portfolio state, generate PDF, send email or create delivery receipt.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect the iShares endpoint discovery artifact. If a stable product-data or factsheet endpoint is found, add a controlled endpoint-evidence fetcher as a separate non-authoritative artifact.
