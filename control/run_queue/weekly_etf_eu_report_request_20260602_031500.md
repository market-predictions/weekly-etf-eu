# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-02T01:15:00Z
mode: phase4_euronext_js_asset_inspection_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding diagnostic-only Euronext JS asset inspection.

## Expected behavior

- run all existing EU bootstrap validations;
- build and validate Euronext endpoint evidence;
- build and validate Euronext product-page evidence;
- build and validate Euronext dynamic quote response discovery;
- build and validate Euronext JS asset inspection;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact including JS asset inspection;
- keep route sampling, candidate closes, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
