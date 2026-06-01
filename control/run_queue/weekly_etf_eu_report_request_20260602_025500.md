# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-02T00:55:00Z
mode: phase4_euronext_dynamic_quote_response_discovery_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding diagnostic-only Euronext dynamic quote response discovery from dynamic_quotes_display.

## Expected behavior

- run all existing EU bootstrap validations;
- build and validate Euronext endpoint evidence;
- build and validate Euronext product-page evidence;
- build and validate Euronext dynamic quote response discovery;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact including dynamic quote response discovery;
- keep candidate closes, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
