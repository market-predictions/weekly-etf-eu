# Workflow wrapper wiring decision — 2026-06-04

## Decision

The agreement-aware valuation wrapper and the pricing-surface renderer wrapper are safe to wire into the EU bootstrap validation workflow, but the direct workflow replacement was blocked by the tool safety layer.

## Intended safe workflow changes

Replace the valuation artifact build step with:

```bash
python -m pricing.build_ucits_valuation_prices_with_agreement \
  --registry config/ucits_symbol_registry.yml \
  --source-policy config/ucits_pricing_source_policy.yml \
  --candidate-artifact "output/pricing/ucits_pricing_candidates_${ETF_EU_RUN_ID}.json" \
  --preflight-artifact "output/pricing/ucits_pricing_preflight_${ETF_EU_RUN_ID}.json" \
  --output-dir output/pricing \
  --run-id "$ETF_EU_RUN_ID"
```

Replace the report render step with:

```bash
python -m runtime.render_etf_eu_report_with_pricing_surface \
  --output-dir output \
  --state output/etf_eu_portfolio_state.json \
  --proxy-map config/ucits_benchmark_proxy_map.yml \
  --registry config/ucits_symbol_registry.yml \
  --pricing-preflight "output/pricing/ucits_pricing_preflight_${ETF_EU_RUN_ID}.json" \
  --valuation-artifact "output/pricing/ucits_valuation_prices_${ETF_EU_RUN_ID}.json" \
  --report-date "$ETF_EU_REPORT_DATE"
```

Extend report validation with:

```bash
python tools/validate_etf_eu_pricing_surface.py "output/weekly_etf_eu_review_${ETF_EU_REPORT_DATE//-/}.md"
python tools/validate_etf_eu_pricing_surface.py "output/weekly_etf_eu_review_nl_${ETF_EU_REPORT_DATE//-/}.md"
```

## Authority boundaries

The wiring must preserve:

```text
valuation_grade=false
valuation_grade_row_count=0
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

## Current implementation state

Already implemented on main:

```text
pricing/build_ucits_valuation_prices_with_agreement.py
runtime/render_etf_eu_report_with_pricing_surface.py
runtime/etf_eu_pricing_surface.py
tools/validate_etf_eu_pricing_surface.py
tests/test_etf_eu_pricing_surface.py
tests/test_etf_eu_report_pricing_surface_wrapper.py
```

## Remaining workflow action

Apply the intended workflow change manually or retry with a narrower patch tool. Do not introduce SMTP, PDF rendering, delivery receipt, portfolio mutation, or candidate promotion in the same change.
