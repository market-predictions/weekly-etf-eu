# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-01T21:15:00Z
mode: phase4_close_engine_adapter_diagnostics_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after improving generic close-engine adapter diagnostics.

## Expected behavior

- validate EU control/config/state files;
- build pricing candidates and preflight artifacts;
- build valuation-pricing artifact;
- build official exchange evidence;
- build and validate generic close observations;
- persist non-delivery artifacts;
- keep portfolio mutation, funding authority, valuation authority, PDF generation and email delivery disabled.
