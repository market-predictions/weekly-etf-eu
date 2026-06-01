# Changelog — Phase 4 Yahoo Verified-Fallback Gate Contract

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Yahoo/yfinance verified-fallback contract and diagnostic gate evaluation.

## Current issue

Yahoo/yfinance has shown useful recent closes for configured UCITS symbols, but it cannot be used as raw authority. The repository needs a controlled fallback contract that keeps Yahoo blocked until symbol, currency, freshness, completed session, cross-source evidence and lineage gates pass.

## Change

Added:

- control/YAHOO_VERIFIED_FALLBACK_CONTRACT_V1.md
- pricing/build_yahoo_fallback_gate_evaluation.py
- tools/validate_yahoo_fallback_gate_evaluation.py
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py
- .github/workflows/validate-yahoo-fallback-gates.yml

## Behavior

The new dedicated workflow builds Yahoo UCITS close diagnostics, evaluates fallback gates, validates that every row remains blocked under current policy, writes shadow evidence, and commits the artifacts.

Expected output patterns:

- output/pricing/yahoo_ucits_close_diagnostics_YYYYMMDD_HHMMSS.json
- output/pricing/yahoo_fallback_gate_evaluation_YYYYMMDD_HHMMSS.json
- output/validation/yahoo_fallback_gate_shadow_evidence_YYYYMMDD_HHMMSS.json

## Safety posture

The fallback gate layer is diagnostic-only. It does not create valuation authority, funding authority, portfolio mutation, PDF generation, email delivery or delivery receipt. Under current policy all rows must remain blocked because fallback policy, completed-session validation and cross-source checks are not yet enabled.

## Next action

Queue the dedicated Yahoo fallback gate workflow. Inspect whether the gate artifact confirms Yahoo prices are fresh while still failing the policy/session/cross-source gates.
