# Changelog — Phase 4 iShares Endpoint Evidence

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Controlled iShares endpoint evidence fetcher for issuer reference diagnostics.

## Current issue

The iShares reference endpoint discovery artifact found candidate endpoints such as product-data.jsn, product-screener-v3.jsn, cwpScreenerApi and productScreenerV3Api. The next safe step is to sample only those allowlisted endpoints and record whether they return structured data and relevant field-name signals.

## Change

Added:

- pricing/build_ishares_endpoint_evidence.py
- tools/validate_ishares_endpoint_evidence.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now builds a diagnostic iShares endpoint evidence artifact. It samples only allowlisted endpoint candidates discovered by the previous endpoint discovery layer:

- product-data.jsn
- product-screener-v3.jsn
- cwpScreenerApi
- productScreenerV3Api

The artifact records bounded metadata:

- HTTP status and content type;
- whether JSON/structured data is observed;
- whether ISIN, product-name, ticker, NAV, reference-date or currency field-name signals are present;
- whether expected product identity tokens appear.

## Safety posture

The endpoint evidence artifact does not include body samples, does not extract NAV/reference price values, does not pass the cross-source gate, does not create valuation authority, does not create funding authority, does not mutate portfolio state, does not generate PDF and does not send email.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether any allowlisted iShares endpoint returns structured data containing ISIN/product/date/currency field-name signals.
