# Changelog — Phase 4 iShares Endpoint Structure Probe

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Bounded iShares endpoint structure probe for issuer reference diagnostics.

## Current issue

The iShares endpoint evidence layer showed that cwpScreenerApi and productScreenerV3Api return HTTP 200 and contain useful field-name signals for ISIN, currency, NAV, product name and ticker, but the responses are HTML rather than parseable JSON.

## Change

Added:

- pricing/build_ishares_endpoint_structure_probe.py
- tools/validate_ishares_endpoint_structure_probe.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now probes only:

- cwpScreenerApi
- productScreenerV3Api

The probe records bounded structural evidence:

- script/table/row/data-attribute counts;
- approximate JSON-like brace count;
- label counts for ISIN, ticker, NAV, currency, date, fund name, product name and price;
- whether a controlled parser follow-up appears worthwhile.

## Safety posture

The structure probe is diagnostic-only. It does not include body samples, does not extract reference-price, NAV, date or currency values, does not create a cross-source pass, does not create valuation authority, does not create funding authority, does not mutate portfolio state, does not generate PDF and does not send email.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether the structure probe indicates a controlled parser follow-up is worthwhile for cwpScreenerApi or productScreenerV3Api.
