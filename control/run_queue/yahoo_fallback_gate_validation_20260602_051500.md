# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T03:15:00Z
mode: phase4_issuer_reference_sanity_gate_validation

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after adding the diagnostic issuer/reference sanity gate.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo completed-session gate;
- build and validate Twelve Data symbol discovery;
- build and validate Yahoo cross-source gate;
- build and validate issuer reference sanity gate;
- build and validate Yahoo fallback gate shadow evidence including issuer sanity evidence;
- keep all rows blocked if no independent trading-line close or issuer reference price sanity evidence is available;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
