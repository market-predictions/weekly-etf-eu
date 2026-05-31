# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-01T22:55:00Z
mode: phase4_euronext_product_page_signal_diagnostics_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding typed Euronext product-page signal diagnostics inside the generic close-price engine adapter.

## Expected behavior

- run all existing EU bootstrap validations;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact;
- persist close-observation diagnostics with Euronext product-page signal diagnostics;
- keep candidate closes non-authoritative;
- keep portfolio mutation, funding authority, valuation authority, PDF generation and email delivery disabled.
