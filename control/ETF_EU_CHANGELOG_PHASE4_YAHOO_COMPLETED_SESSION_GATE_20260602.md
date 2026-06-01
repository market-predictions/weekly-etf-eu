# Changelog — Phase 4 Yahoo Completed-Session Gate

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Diagnostic completed-session validation gate for Yahoo/yfinance UCITS fallback rows.

## Current issue

Yahoo/yfinance has fresh close diagnostics for CSPX.AS, CSPX.L and SXR8.DE, but the fallback contract still requires proof that the observed close date corresponds to a completed regular trading session for the relevant venue.

## Change

Added:

- config/ucits_exchange_session_policy.yml
- pricing/build_yahoo_completed_session_gate.py
- tools/validate_yahoo_completed_session_gate.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now evaluates whether the Yahoo observed close date is a completed regular session under a deterministic diagnostic venue policy for:

- Euronext Amsterdam / XAMS;
- London Stock Exchange / XLON;
- Xetra / XETR.

The gate checks:

- venue policy exists;
- observed close date exists;
- observed close date is a regular weekday and not a listed static holiday;
- regular venue close plus post-close buffer has elapsed;
- close is within the staleness limit.

Expected output pattern:

- output/pricing/yahoo_completed_session_gate_YYYYMMDD_HHMMSS.json

## Safety posture

This gate is diagnostic-only. It does not create valuation authority, funding authority, portfolio mutation, PDF generation, email delivery or delivery receipt.

Even if completed-session validation passes, Yahoo fallback remains blocked until fallback policy is enabled and a cross-source check passes.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether all three rows validate the completed-session gate while remaining blocked by the cross-source gate.
