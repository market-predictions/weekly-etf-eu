# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-06-04

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Current phase

```text
Phase 7 — main EU bootstrap workflow verified on agreement-aware wrapper path
```

## Verified evidence

WP1 shadow workflow proof:

```text
output/validation/etf_eu_pricing_surface_shadow_20260604_213059.json
```

WP4 main workflow proof:

```text
GitHub Actions run #34 on main: success
artifact commit: 373bffb74745047aa79f3109ae62afd79e03abe1
output/validation/etf_eu_shadow_validation_evidence_20260604_220814.json
```

Key artifacts from the verified run:

```text
output/weekly_etf_eu_review_260604.md
output/weekly_etf_eu_review_nl_260604.md
output/pricing/ucits_valuation_prices_20260604_220814.json
```

## Current workflow posture

The main EU bootstrap workflow now uses:

```text
pricing.build_ucits_valuation_prices_with_agreement
runtime.render_etf_eu_report_with_pricing_surface
```

The workflow also validates the pricing surface and fundability contract.

## Pending items

1. Production Dutch-first report surface.
2. Later operational send path only after a separate manifest/receipt path exists.

## Boundary rule

The authority boundaries from `control/DECISION_LOG.md` remain unchanged.
