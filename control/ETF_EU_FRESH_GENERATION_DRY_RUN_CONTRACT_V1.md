# ETF EU Fresh Generation Dry Run Contract V1

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1`

## Purpose

Define the no-send fresh-generation dry-run path for the Weekly ETF EU routine loop.

The goal is to prove that `weekly-etf-eu` can create a fresh Dutch-primary / English-companion EU report package scaffold from EU-authoritative state without reusing the one-off `ETF-EU-MVP19-FIX2` controlled resend package as the package source of truth.

```text
upstream_pattern_adapted=weekly-etf fresh-generation/runtime/report-manifest concept; adapted for EU dry-run and UCITS authority boundaries
```

## Scope

MVP23 covers:

```text
EU state
→ UCITS pricing / pricing evidence reference
→ Dutch-primary markdown dry-run scaffold
→ English-companion markdown dry-run scaffold
→ HTML dry-run scaffold
→ package manifest
→ ready-for-controlled-delivery dry-run artifact
→ EU routine run manifest handoff
```

MVP23 does not send email, dispatch a workflow, create a run queue file, mutate portfolio state, create funded positions, promote valuation-grade pricing, or create production-delivery authority.

## Authority boundaries

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

Allowed:

```text
decision_allowed=research_review
candidate_review_allowed=true
client_facing_research_allowed=true
```

Not allowed:

```text
allocation_allowed=false
trade_allowed=false
portfolio_mutation_allowed=false
candidate_auto_promotion=false
fresh_capital_deployment=false
valuation_grade_promotion=false
funding_authority=false
production_delivery_authority=false
```

## EU input/state contract

EU-authoritative inputs:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
config/nl_client_investability_rules.yml
config/etf_eu_discovery_universe.yml
output/run_manifests/latest_etf_eu_routine_run_manifest_path.txt
output/run_manifests/latest_etf_eu_delivery_closeout_manifest_path.txt
```

Optional pricing evidence:

```text
output/pricing/ucits_close_price_validation_basket_results_*.json
```

Rejected as EU authority:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
weekly_analysis_pro_*.md as EU source truth
U.S. ETF tickers as investable EU holdings
```

## Output contract

MVP23 writes fresh dry-run files under `output/fresh_generation/`.

Required artifact classes:

```text
Dutch primary markdown dry-run scaffold
English companion markdown dry-run scaffold
Dutch primary HTML dry-run scaffold
English companion HTML dry-run scaffold
fresh-generation package manifest
ready-for-controlled-delivery dry-run artifact
updated EU routine run manifest
```

PDF generation is explicitly not implemented in MVP23 unless a safe EU renderer is proven available:

```text
pdf_generation_status=not_implemented_in_mvp23
ready_for_controlled_delivery=false
```

Required output properties:

```text
dutch_primary=true
english_companion=true
isin_first_identity=true
us_etfs_proxy_only=true
main_surface_us_holdings_exposure=false
nan_price_in_client_surface=false
stale_delivery_wording_present=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

## Pricing evidence handling

MVP23 may reference the latest committed UCITS pricing evidence if present. It may not promote pricing evidence to valuation authority.

```text
pricing_evidence_role=diagnostic_or_reference_only
valuation_grade=false
funding_authority=false
portfolio_mutation=false
```

## Ready-for-controlled-delivery rules

The MVP23 dry-run ready artifact must keep:

```text
ready_for_controlled_delivery=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

A later package may promote a generated package to controlled-delivery readiness only after full fresh renderer/package validators pass.

## Routine run manifest handoff

MVP23 must update the EU routine run manifest with fresh-generation artifact paths and keep:

```text
routine_stage=fresh_generation_dry_run_scaffold
fresh_generation_and_guarded_delivery_kept_separate=true
transport_attempted=false
transport_success=false
receipt_confirmed=false
next_package=ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
```

## Non-delivery guardrails

MVP23 must not:

```text
send another email
dispatch workflow
create run queue file
mutate portfolio state
create funded UCITS positions
store raw Gmail PDF in GitHub
copy U.S. ETF portfolio state
use U.S. ETF tickers as investable EU holdings
treat MVP19-FIX2 package as fresh generation
merge fresh generation and delivery into one production workflow
```
