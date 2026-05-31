# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-06-01T21:40:00Z
mode: shadow_validation_evidence_validation

## Purpose

Queue the Weekly ETF EU UCITS bootstrap validation workflow after adding the repo-native shadow validation evidence artifact.

## Expected behavior

- run all existing EU bootstrap validations;
- build non-production pricing/report artifacts;
- build and validate `output/validation/etf_eu_shadow_validation_evidence_*.json`;
- commit the shadow validation evidence artifact to GitHub;
- keep portfolio mutation, funding authority, valuation authority, PDF generation and email delivery disabled.
