# Yahoo fallback gate validation request

requested_at_utc: 2026-06-02T03:50:00Z
mode: phase4_ishares_reference_endpoint_discovery_validation

## Purpose

Queue the dedicated Yahoo fallback gate validation workflow after adding diagnostic iShares reference endpoint discovery.

## Expected behavior

- build and validate Yahoo UCITS close diagnostics;
- build and validate Yahoo fallback gate evaluation;
- build and validate Yahoo completed-session gate;
- build and validate Twelve Data symbol discovery;
- build and validate Yahoo cross-source gate;
- build and validate issuer reference sanity gate;
- build and validate iShares reference endpoint discovery;
- build and validate Yahoo fallback gate shadow evidence including iShares endpoint discovery evidence;
- extract no issuer NAV/reference price;
- create no valuation authority, funding authority, portfolio mutation, PDF generation or email delivery.
