# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T03:30:00Z
mode: phase4_issuer_reference_sanity_gate_validation_after_validator_fix

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after relaxing the issuer-reference sanity gate validator so identity misses are recorded as blocked diagnostic gates rather than workflow failures.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo completed-session gate;
- build and validate Twelve Data symbol discovery;
- build and validate Yahoo cross-source gate;
- build and validate issuer reference sanity gate;
- record issuer identity/reference-price misses as blocked gates;
- build and validate Yahoo fallback gate shadow evidence;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
