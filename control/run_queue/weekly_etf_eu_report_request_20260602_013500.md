# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-01T23:35:00Z
mode: phase4_euronext_quote_endpoint_candidate_evidence_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding diagnostic-only Euronext quote endpoint candidate evidence derived from the custom instrument summary.

## Expected behavior

- run all existing EU bootstrap validations;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact;
- persist Euronext quote endpoint candidate evidence in the close-observation artifact;
- keep endpoint fetching, candidate closes, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
