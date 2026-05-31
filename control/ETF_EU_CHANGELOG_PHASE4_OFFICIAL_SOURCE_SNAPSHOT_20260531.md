# Weekly ETF EU Review OS — Phase 4 Official Source Snapshot Changelog

Date: 2026-05-31
Repository: market-predictions/weekly-etf-eu
Scope: Pivot away from Twelve Data upgrade path and register official exchange source candidates.

## Current issue

Twelve Data recognized UCITS symbols, but CSPX/LSE time-series data is plan-gated on the current tier and the user explicitly decided not to upgrade the Twelve Data plan.

## Root cause

Twelve Data can remain useful for diagnostics, but it should not be the primary authority path for EU UCITS valuation under the current operating constraints.

## Recommended change implemented

The pricing source policy now prefers official exchange source candidates:

- Euronext Amsterdam / XAMS for the Dutch/EU EUR line.
- Deutsche Boerse / Xetra for the SXR8 EUR line.

Twelve Data remains diagnostic and blocked from valuation-grade promotion by accept_as_valuation_grade=false.

## Files changed

- config/ucits_pricing_source_policy.yml
- pricing/build_ucits_valuation_prices.py
- tools/validate_ucits_valuation_prices.py
- .github/workflows/send-weekly-etf-eu-report.yml

## Files added

- pricing/build_official_exchange_source_snapshot.py
- tools/validate_official_exchange_source_snapshot.py

## Output artifact added

The workflow now writes:

output/pricing/ucits_official_exchange_source_snapshot_YYYYMMDD_HHMMSS.json

This artifact is diagnostic only. It records official source candidates and preserves:

- portfolio_mutation=false
- production_delivery=false
- funding_authority=false
- valuation_authority=false

## What this does not do

This patch does not scrape exchange pages, mark prices as valuation-grade, mutate portfolio state, fund a UCITS ETF, render a production PDF, or send email.

## Next action

Run the EU bootstrap validation workflow and verify that the new official exchange source snapshot is generated and committed.
