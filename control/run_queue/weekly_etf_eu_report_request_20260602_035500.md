# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-02T01:55:00Z
mode: phase4_yahoo_ucits_close_diagnostics_validation_after_shadow_builder_restore

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after restoring the shadow validation evidence builder and adding non-authoritative Yahoo/yfinance UCITS close diagnostics.

## Expected behavior

- run all existing EU bootstrap validations;
- build and validate Euronext diagnostic evidence layers;
- build and validate Yahoo UCITS close diagnostics from configured yahoo_yfinance policy symbols;
- build non-production pricing/report artifacts;
- build and validate the shadow validation evidence artifact including Yahoo diagnostics;
- keep Yahoo connectivity-only, with candidate close extraction, completed-session validation, valuation authority, funding authority, portfolio mutation, PDF generation and email delivery disabled.
