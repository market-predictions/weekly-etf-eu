# UCITS Valuation Pricing Contract V1

## Purpose

This contract defines the valuation-grade UCITS pricing authority layer for `market-predictions/weekly-etf-eu`.

## Yahoo/yfinance boundary

Yahoo/yfinance may be used as temporary connectivity/display evidence only.

Under the current policy, Yahoo/yfinance:

```text
is not agreement-gate valuation-grade authority
does not count as independent market-close agreement evidence
must not satisfy min_independent_sources
must not populate valuation authority fields
must not flip valuation_grade to true
```

## Input/state contract

Authoritative inputs include:

```text
config/ucits_symbol_registry.yml
config/ucits_pricing_source_policy.yml
control/DATA_SOURCE_METADATA.md
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
```

## Output contract

Every artifact and row must preserve:

```text
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

## Non-mutation rule

This valuation layer is evidence production only. Pricing authority alone is never portfolio authority.
