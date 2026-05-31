# Weekly ETF EU Review OS — Phase 4 Generic Close Price Engine Scaffold Changelog

Date: 2026-05-31
Repository: market-predictions/weekly-etf-eu
Scope: Convert source-specific page research into a generic ISIN/trading-line/source-adapter close-price engine scaffold.

## Current issue

The Euronext and Deutsche Boerse work proved useful for source discovery, but continuing to grow page-specific parsing inside the page-evidence builder would create a brittle one-off scraper instead of a reusable EU UCITS closing-price engine.

## Root cause

European UCITS ETF pricing is not ticker-first. A generic engine must route from ISIN-first trading-line identity into reusable source adapters.

The engine key should be:

registry_id + isin + exchange + exchange_ticker + trading_currency + source_id + adapter_name

## Change implemented

Added a generic close-price engine scaffold.

## Files added

- control/UCITS_CLOSE_PRICE_ENGINE_CONTRACT_V1.md
- pricing/close_engine/contracts.py
- pricing/close_engine/engine.py
- pricing/close_engine/adapters/__init__.py
- pricing/close_engine/adapters/euronext.py
- pricing/close_engine/adapters/deutsche_boerse.py
- tools/validate_ucits_close_observations.py

## Files changed

- .github/workflows/send-weekly-etf-eu-report.yml

## Output artifact added

The workflow now writes:

output/pricing/ucits_close_observations_YYYYMMDD_HHMMSS.json

## Current behavior

The first adapters are scaffolds only:

- euronext_live
- deutsche_boerse_live

They emit standardized observation rows with blockers and no candidate close/date authority.

## Authority flags preserved

- portfolio_mutation=false
- production_delivery=false
- funding_authority=false
- valuation_authority=false
- completed_session=false
- candidate_close=null
- candidate_date=null

## What this does not do

This does not parse a clean closing price, create valuation-grade rows, fund positions, write valuation history, render production PDFs, or send email.

## Next action

Validate the generic scaffold in GitHub Actions, then implement adapter-specific parsing behind the generic interface, starting with the most stable source path.
