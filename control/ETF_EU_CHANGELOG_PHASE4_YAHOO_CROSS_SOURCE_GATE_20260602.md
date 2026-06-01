# Changelog — Phase 4 Yahoo Cross-Source Gate

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Diagnostic cross-source gate for Yahoo/yfinance UCITS fallback rows.

## Current issue

Yahoo/yfinance rows now have fresh closes and completed-session evidence, but the verified-fallback contract still requires an independent cross-source check before any fallback review can be considered.

## Change

Added:

- pricing/build_yahoo_cross_source_gate.py
- tools/validate_yahoo_cross_source_gate.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now:

1. builds Yahoo UCITS close diagnostics;
2. builds Yahoo fallback gate evaluation;
3. builds Yahoo completed-session gate;
4. runs Twelve Data symbol discovery;
5. builds a Yahoo cross-source gate comparing same trading-line Yahoo rows against Twelve Data evidence;
6. persists all artifacts and shadow evidence.

The current expected result is blocked, because Twelve Data discovery finds identity candidates but does not provide independent time-series closes under the current tier/policy.

Expected output pattern:

- output/pricing/yahoo_cross_source_gate_YYYYMMDD_HHMMSS.json

## Safety posture

The cross-source gate is diagnostic-only. It does not create valuation authority, funding authority, portfolio mutation, PDF generation, email delivery or delivery receipt.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether the gate remains blocked for lack of independent close data. If blocked, the next strategic decision is whether to use another independent source for cross-checking or keep Yahoo as diagnostics-only.
