# Weekly ETF EU Review OS — Phase 4 Official Page Evidence Changelog

Date: 2026-05-31
Repository: market-predictions/weekly-etf-eu
Scope: Validate official exchange page identity evidence without extracting prices or creating valuation authority.

## Current issue

Twelve Data is not being upgraded and is no longer the preferred valuation-source path. The repo needs an official-source path that can verify exchange-page identity before any price extraction is attempted.

## Root cause

Official exchange source URLs must be verified as the correct UCITS trading-line pages before any price field can be trusted. URL existence alone is insufficient, and a page fetch must not automatically become price or funding authority.

## Change implemented

Added an official exchange page-evidence layer that fetches the configured official source pages and checks expected identity tokens.

## Files added

- pricing/build_official_exchange_page_evidence.py
- tools/validate_official_exchange_page_evidence.py

## Files changed

- .github/workflows/send-weekly-etf-eu-report.yml

## Output artifact added

The workflow now writes:

output/pricing/ucits_official_exchange_page_evidence_YYYYMMDD_HHMMSS.json

## Latest validated artifact

Run id:

20260531_203242

Persisted artifact commit:

1cb3b5f207405dac1dd2237eb72db30cf7a13071

Observed evidence:

- Euronext Amsterdam / CSPX / XAMS page reachable, HTTP 200, expected identity tokens present.
- Deutsche Boerse / Xetra / SXR8 page reachable, HTTP 200, ISIN and ticker tokens present; the literal expected currency token needs normalization before it should be treated as exact proof.

## Authority flags preserved

- portfolio_mutation=false
- production_delivery=false
- funding_authority=false
- valuation_authority=false
- price_extraction=false

## What this does not do

This does not extract prices, create valuation-grade rows, fund positions, write valuation history, generate PDFs, or send email.

## Next action

Add a controlled official-page price-observation layer. It should capture candidate price/date/currency text from official pages as evidence only, keep valuation_authority=false, and require separate validation before any promotion to valuation-grade authority.
