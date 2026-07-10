# ETF EU Routine Weekly Operating Loop V1

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1`

## Purpose

Define the repeatable Weekly ETF EU operating loop after the first controlled resend was receipt-confirmed and post-delivery closeout was hardened.

The EU loop is not a translated copy of the U.S. ETF production loop. It borrows mature upstream `weekly-etf` runtime, manifest, validation, and delivery evidence concepts, while preserving EU/UCITS authority boundaries.

```text
upstream_pattern_adapted=weekly-etf routine workflow and run-manifest pattern; adapted for EU/UCITS authority boundaries
```

## Scope

The routine loop covers:

```text
pricing
→ EU/UCITS package generation/readiness
→ Dutch-primary + English-companion output package
→ guarded delivery only after explicit authorization
→ persisted transport evidence
→ receipt/closeout manifest
→ next-run state handoff
```

This contract does not authorize sending, report regeneration, portfolio mutation, funding, or valuation-grade promotion by itself.

## Authority boundaries

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

A routine EU report may review UCITS candidates and produce client-facing research.

It may not:

```text
allocation_allowed=false
trade_allowed=false
portfolio_mutation_allowed=false
funding_authority=false
valuation_grade=false unless explicit EU agreement gate passes
production_delivery_authority=false unless explicit guarded delivery evidence and receipt/manifest proof exist
```

U.S. ETF files, holdings, report filenames, delivery authority, and portfolio state are architecture donors only. They are not EU state authority.

## Four-layer model

### 1. Decision framework

Allowed:

```text
decision_allowed=research_review
candidate_review_allowed=true
client_facing_research_allowed=true
```

Not allowed by this contract:

```text
allocation_allowed=false
trade_allowed=false
portfolio_mutation_allowed=false
candidate_auto_promotion=false
fresh_capital_deployment=false
valuation_grade_promotion=false
funding_authority=false
```

Any future funding, valuation-grade, allocation, or portfolio mutation must be authorized by a separate explicit decision package and validator.

### 2. Input/state contract

Canonical EU inputs:

```text
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
config/nl_client_investability_rules.yml
config/etf_eu_discovery_universe.yml
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
output/pricing/ucits_close_price_validation_basket_results_*.json
output/run_manifests/etf_eu_delivery_closeout_manifest_*.json
```

Routine run input names:

```text
previous_delivery_closeout_manifest
previous_portfolio_state
current_ucits_pricing_artifact
current_report_package_manifest
current_ready_for_delivery_artifact
```

State authority rules:

```text
previous_portfolio_state=output/etf_eu_portfolio_state.json
u_s_portfolio_state_authority=false
cash_only_state_allowed=true
positions_allowed_only_after_future_funding_gate=false
```

### 3. Output contract

A routine weekly EU run must be able to produce, before any delivery:

```text
Dutch primary markdown
English companion markdown
Dutch primary HTML
English companion HTML
Dutch primary PDF
English companion PDF
EU delivery package manifest
EU ready-for-controlled-delivery artifact
EU routine run manifest
```

Output requirements:

```text
dutch_primary=true
english_companion=true
isin_first_identity=true
us_etfs_proxy_only=true
main_surface_us_holdings_exposure=false
nan_price_in_client_surface=false
stale_delivery_wording_present=false
valuation_grade=false unless explicit EU agreement gate passes
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

### 4. Operational runbook

Routine stages:

```text
1. Pull latest main and verify clean state.
2. Resolve report date / requested close date.
3. Run EU/UCITS pricing or pricing validation.
4. Build EU report/package from authoritative EU inputs.
5. Validate Dutch-primary and English-companion outputs.
6. Render HTML/PDF package.
7. Write delivery package manifest.
8. Write ready-for-controlled-delivery artifact.
9. Write EU routine run manifest.
10. Stop before send unless delivery is explicitly authorized.
11. If explicitly authorized, run guarded send only through workflow dispatch.
12. Persist transport evidence, receipt check artifact, and closeout manifest.
13. Update CURRENT_STATE.md and NEXT_ACTIONS.md only after evidence exists.
```

Recommended MVP22 implementation decision:

```text
fresh_generation_and_guarded_delivery_kept_separate=true
selected_design_option=option_b_define_future_fresh_weekly_workflow_without_implementation
```

## Delivery evidence requirements

A guarded delivery may not be marked successful unless machine-readable evidence records:

```text
transport_attempted=true
transport_success=true
message_id_or_receipt_reference populated
recipient_plaintext_values_exposed=false
secret_values_exposed=false
```

A receipt may not be marked confirmed unless a receipt or closeout manifest exists:

```text
receipt_confirmed=true requires delivery_closeout_manifest
```

SMTP success remains transport evidence only. It is not by itself an end-recipient inbox receipt.

## Next-run handoff

Every routine run must write or update:

```text
output/run_manifests/etf_eu_routine_run_manifest_<REPORT_DATE>_<RUN_ID>.json
output/run_manifests/latest_etf_eu_routine_run_manifest_path.txt
```

The next run should read the latest routine manifest plus the latest delivery closeout manifest and EU portfolio state before deciding whether to generate a fresh package, request human authorization, or stop.

## Non-goals

This contract does not:

```text
send email
dispatch workflow
create run queue files
regenerate a report
mutate portfolio state
create funded UCITS positions
store raw Gmail PDF in GitHub
copy U.S. ETF portfolio state
copy U.S. delivery authority
merge fresh generation and delivery into one production workflow
```
