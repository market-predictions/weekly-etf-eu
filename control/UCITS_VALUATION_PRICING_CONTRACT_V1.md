# UCITS Valuation Pricing Contract V1

## Purpose

This contract defines the valuation-grade UCITS pricing authority layer for `market-predictions/weekly-etf-eu`.

It sits after the non-authoritative UCITS pricing-line preflight and before any future portfolio funding, valuation-history mutation, report delivery, PDF generation or email send.

The contract exists to prevent this failure mode:

```text
a reachable quote symbol is accidentally treated as authoritative portfolio valuation
```

## Input/state contract

The authoritative inputs are:

```text
config/ucits_symbol_registry.yml
config/ucits_pricing_source_policy.yml
control/DATA_SOURCE_METADATA.md
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
```

The non-authoritative preflight may be used as evidence of connectivity or display continuity only. It cannot create a valuation-grade row unless source policy, source metadata, and agreement-gate rules explicitly allow that source for that exact trading line.

## Output contract

Every artifact and row must state:

```text
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

A row may claim `valuation_grade: true` only if the validator confirms required source, date, close, currency, completed-session and source-lineage evidence, and only if the agreement gate confirms sufficient independent market-close agreement evidence under source metadata policy.

## Source authority hierarchy

Default hierarchy:

1. `exchange_official` / venue-specific official exchange candidates — preferred valuation source when a completed-session official close is available and attributable.
2. `twelve_data` — diagnostic/candidate source only after symbol/date/currency evidence and plan/source terms are verified for the specific UCITS trading line.
3. `issuer_factsheet` / issuer NAV references — reference-only or stale-check sources, not daily close authority unless explicitly upgraded by a separate contract.
4. `yahoo_yfinance` — non-authoritative connectivity/display source by default.

Under the current policy, `yahoo_yfinance` cannot be agreement-gate valuation-grade authority.

## Agreement-gate source-counting rule

A source may count as independent market-close agreement evidence only when source metadata and source policy both allow it.

Current non-counting sources include:

```text
yahoo_yfinance
issuer_nav
blackrock_issuer_reference
issuer_factsheet
stooq
boerse_frankfurt
twelve_data
```

A Yahoo/yfinance observed close may be preserved as provisional connectivity/display evidence, but it must not satisfy `min_independent_sources`, must not populate valuation authority fields, and must not flip `valuation_grade` to `true` under the current agreement-gate policy.

## Non-mutation rule

This valuation layer is evidence production only.

It must not update:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
```

until a later funding/promotion contract exists.

Pricing authority alone is never portfolio authority.
