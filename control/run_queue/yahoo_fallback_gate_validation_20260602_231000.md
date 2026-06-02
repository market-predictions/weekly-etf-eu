# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T21:10:00Z
mode: phase4_ishares_reference_value_candidates_validation

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after adding the non-authoritative iShares reference value-candidate artifact.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo completed-session gate;
- build and validate Twelve Data symbol discovery;
- build and validate Yahoo cross-source gate;
- build and validate issuer reference sanity gate;
- build and validate iShares reference endpoint discovery;
- build and validate iShares endpoint evidence;
- build and validate iShares endpoint structure probe;
- build and validate iShares controlled parser probe;
- build and validate iShares reference value candidates as label/selector/context-hash candidates only;
- build and validate Yahoo fallback gate shadow evidence including value-candidate evidence;
- extract no issuer NAV/reference price/date/currency values;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
