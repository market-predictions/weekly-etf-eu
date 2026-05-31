# Changelog — Phase 4 Euronext Quote Endpoint Candidate Evidence

Date: 2026-06-01
Repository: market-predictions/weekly-etf-eu
Scope: diagnostic-only Euronext quote endpoint candidate evidence.

## Current issue

The Euronext adapter now emits a structured custom instrument summary, but the workflow still needed a machine-readable candidate list for the next controlled endpoint evidence step.

## Change

Added:

- pricing/close_engine/adapters/euronext_quote_endpoint_candidates.py

Updated:

- pricing/close_engine/engine.py

The new helper builds quote endpoint candidate evidence from the verified custom instrument identity. The engine post-processes Euronext close-observation rows and adds this evidence under product_page_signal_diagnostics.

## Safety posture

This change does not fetch any extra endpoint. It does not parse a close price. It does not validate completed session. It does not create valuation authority, funding authority, portfolio mutation, PDF generation, email delivery, or production delivery.

The evidence is candidate-only and diagnostic-only.

## Next action

Run the bootstrap workflow and inspect the new close-observation artifact. If the candidate evidence is stable, choose one candidate URL for a future controlled evidence-fetch patch. That future patch must still remain blocked from valuation authority until close, date, currency, completed session, lineage, and staleness are separately validated.
