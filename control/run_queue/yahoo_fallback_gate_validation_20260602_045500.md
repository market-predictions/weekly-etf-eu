# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T02:55:00Z
mode: phase4_yahoo_cross_source_gate_validation

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after adding the cross-source gate against Twelve Data discovery evidence.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo completed-session gate;
- build and validate Twelve Data symbol discovery;
- build and validate Yahoo cross-source gate;
- build and validate Yahoo fallback gate shadow evidence including cross-source gate evidence;
- keep all rows blocked if no independent close/date/currency comparison is available;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
