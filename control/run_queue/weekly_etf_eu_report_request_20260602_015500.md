# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-01T23:55:00Z
mode: phase4_euronext_endpoint_evidence_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding controlled single-candidate Euronext endpoint evidence.

## Expected behavior

- run all existing EU bootstrap validations;
- build and validate Euronext endpoint evidence for settings_search_product_data;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact including endpoint evidence;
- keep candidate closes, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
