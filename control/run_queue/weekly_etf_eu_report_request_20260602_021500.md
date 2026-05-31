# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-02T00:15:00Z
mode: phase4_euronext_search_html_inspection_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding diagnostic-only HTML inspection to the Euronext endpoint evidence artifact.

## Expected behavior

- run all existing EU bootstrap validations;
- build and validate Euronext endpoint evidence with canonical/link/card/loopback inspection;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact including endpoint evidence;
- keep candidate closes, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
