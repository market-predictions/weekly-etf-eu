# Changelog — Phase 4 Issuer Reference Sanity Gate

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Diagnostic issuer/reference sanity gate for Yahoo/yfinance fallback rows.

## Current issue

Yahoo/yfinance has fresh close, currency, lineage and completed-session evidence for configured UCITS rows, but the free Twelve Data path does not provide independent time-series closes for the cross-source gate. The next safe diagnostic layer is an issuer/reference sanity gate.

## Change

Added:

- config/issuer_reference_policy.yml
- pricing/build_issuer_reference_sanity_gate.py
- tools/validate_issuer_reference_sanity_gate.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now fetches the configured issuer product page and records bounded diagnostic evidence:

- issuer policy presence;
- issuer page fetch status;
- ISIN/product identity token match;
- whether issuer reference price/NAV evidence is available;
- whether broad reference tolerance can be evaluated.

Expected output pattern:

- output/pricing/issuer_reference_sanity_gate_YYYYMMDD_HHMMSS.json

## Safety posture

Issuer reference sanity evidence is not a trading-line official close source. It cannot create valuation authority, funding authority, portfolio mutation, PDF generation, email delivery or delivery receipt.

The current gate intentionally remains blocked because reference price/NAV extraction is not implemented in this version and the cross-source gate is already blocked.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether issuer identity is found. If identity is found but reference price is not, decide whether to add controlled issuer NAV extraction or keep Yahoo diagnostic-only until official exchange close evidence is available.
