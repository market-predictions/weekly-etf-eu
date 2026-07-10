# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION**.

## Latest completion

```text
work_package_id=ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN
status=completed_fresh_generation_dry_run_scaffold
source_work_package=ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf fresh-generation/runtime/report-manifest concept; adapted for EU dry-run and UCITS authority boundaries
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
fresh_generation_dry_run_contract_created=true
fresh_generation_dry_run_contract=control/ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1.md
fresh_generation_dry_run_builder_created=true
fresh_generation_dry_run_builder=tools/build_etf_eu_fresh_generation_dry_run.py
fresh_generation_dry_run_validator_created=true
fresh_generation_dry_run_validator=tools/validate_etf_eu_fresh_generation_dry_run.py
fresh_generation_dry_run_manifest_created=true
fresh_generation_dry_run_manifest=output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
fresh_generation_ready_artifact=output/fresh_generation/etf_eu_ready_for_controlled_delivery_dry_run_20260710_000000.json
fresh_generation_dutch_primary_markdown=output/fresh_generation/weekly_etf_eu_review_nl_260710_dry_run.md
fresh_generation_english_companion_markdown=output/fresh_generation/weekly_etf_eu_review_260710_dry_run.md
fresh_generation_dutch_primary_html=output/fresh_generation/weekly_etf_eu_review_nl_260710_dry_run.html
fresh_generation_english_companion_html=output/fresh_generation/weekly_etf_eu_review_260710_dry_run.html
fresh_generation_status=scaffold_created
full_generation_status=blocked_pending_renderer_or_pricing_integration
pdf_generation_status=not_implemented_in_mvp23
ready_for_controlled_delivery=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
generation_and_delivery_separate=true
send_executed=false
transport_attempted=false
receipt_confirmed_from_new_run=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=fresh_generation_dry_run_scaffold_ready_for_renderer_integration
selected_next_package=ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
```

## Standing upstream-first reuse rule

Before creating or materially changing any ETF EU task, work package, workflow, runtime script, validator, renderer, delivery step, or control file, first inspect the closest upstream `market-predictions/weekly-etf` implementation.

Record one of:

```text
upstream_pattern_reused=<file or concept>
upstream_pattern_adapted=<file or concept + reason>
upstream_pattern_rejected=<file or concept + EU authority reason>
no_upstream_equivalent_found=<search terms / inspected files>
```

Borrow mature concepts and safeguards. Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
```

## ETF-EU-MVP24 objective

Integrate the fresh-generation scaffold with a real EU renderer/package builder so the routine loop can produce a complete Dutch-primary / English-companion package from EU state.

MVP24 should start from the MVP23 scaffold and decide whether to adapt upstream `runtime/build_etf_report_state.py`, `runtime/render_etf_report_from_state.py`, and HTML/PDF delivery asset generation, or keep a thinner EU-specific renderer.

Do not send by default.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md
control/ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` renderer/package patterns before modifying anything:

```text
market-predictions/weekly-etf:runtime/build_etf_report_state.py
market-predictions/weekly-etf:runtime/render_etf_report_from_state.py
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
market-predictions/weekly-etf:tools/write_weekly_etf_run_manifest.py
```

## MVP24 recommended scope

```text
1. Replace MVP23 scaffold-only generation with a real EU renderer path where safe.
2. Preserve Dutch-primary / English-companion output contract.
3. Preserve EU state authority and reject U.S. portfolio state.
4. Add HTML/PDF package generation only after validators prove outputs are clean.
5. Keep guarded delivery separate; no send unless later explicit delivery package authorizes it.
```

## Guardrail

No workflow dispatch, email sending, live delivery, portfolio mutation, valuation-grade promotion, funding authority promotion, or raw Gmail receipt storage should be started from this state update alone.
