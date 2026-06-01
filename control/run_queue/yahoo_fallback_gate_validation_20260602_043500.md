# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T02:35:00Z
mode: phase4_yahoo_completed_session_gate_validation

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after adding the completed-session gate for Yahoo/yfinance UCITS fallback rows.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo completed-session gate;
- build and validate Yahoo fallback gate shadow evidence including completed-session gate evidence;
- keep all rows blocked by fallback policy and cross-source gates;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
