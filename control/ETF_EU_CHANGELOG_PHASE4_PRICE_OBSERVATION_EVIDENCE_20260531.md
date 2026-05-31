# Weekly ETF EU Review OS — Phase 4 Price Observation Evidence Changelog

Date: 2026-05-31
Repository: market-predictions/weekly-etf-eu
Scope: Extend official exchange page evidence with candidate price/date/currency observation text while keeping all authority flags false.

## Current issue

Official exchange pages were reachable and identity-checked, but the workflow did not yet capture any page text that could later be analyzed for price/date/currency evidence.

## Root cause

The EU valuation source path needs a staged evidence ladder:

1. source candidate registered;
2. official page identity verified;
3. candidate price/date/currency text observed;
4. structured price parsed;
5. date/currency/session verified;
6. only then possible valuation-grade promotion.

The previous layer covered steps 1 and 2 only.

## Change implemented

The existing official page-evidence builder now also records candidate snippets around price/date/currency terms.

## Files changed

- pricing/build_official_exchange_page_evidence.py
- tools/validate_official_exchange_page_evidence.py

## Output artifact

The workflow continues to write:

output/pricing/ucits_official_exchange_page_evidence_YYYYMMDD_HHMMSS.json

New row fields include:

- candidate_observation_status
- candidate_price_date_currency_text

## Latest validated result

GitHub Actions run #15 passed and produced persisted artifact commit:

08f523bd3e9a9d3dcecc9d73139846db22383050

Observed behavior:

- Euronext Amsterdam / CSPX page produced candidate text, but snippets are still noisy and include navigation/page metadata.
- Deutsche Boerse / Xetra / SXR8 page produced more useful candidate text, including labels such as Schlusspreis des letzten Handelstages and Handelswährung EUR.

## Authority flags preserved

- price_extraction=false
- portfolio_mutation=false
- production_delivery=false
- funding_authority=false
- valuation_authority=false

## Important limitation

This layer does not parse a clean numeric official close, does not verify completed-session date, and does not create valuation authority. The evidence is useful, but still too noisy for valuation-grade pricing.

## Next action

Refine official-source observation from broad page snippets into source-specific structured extraction:

- Euronext: identify the page endpoint or embedded data structure that contains the official quote table.
- Deutsche Boerse: extract the clean value next to Schlusspreis des letzten Handelstages, its date, and currency.
- Keep all parsed values as candidate evidence only until a separate validator can verify date, currency, source lineage and completed session.
