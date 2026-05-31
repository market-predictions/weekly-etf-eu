# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-01T22:35:00Z
mode: phase4_euronext_product_link_probe_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding Euronext product-link probe diagnostics inside the generic close-price engine adapter.

## Expected behavior

- run all existing EU bootstrap validations;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact;
- persist close-observation diagnostics with Euronext canonical/product-link probe results;
- keep candidate closes non-authoritative;
- keep portfolio mutation, funding authority, valuation authority, PDF generation and email delivery disabled.
