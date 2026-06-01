# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T02:15:00Z
mode: phase4_yahoo_verified_fallback_gate_validation

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after adding the Yahoo verified-fallback contract and gate evaluation layer.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo fallback gate shadow evidence;
- keep all rows blocked under current policy because fallback policy, completed-session validation and cross-source checks are not enabled;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
