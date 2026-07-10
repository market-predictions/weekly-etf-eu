# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE**.

## Latest completion

```text
work_package_id=ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
status=completed_fresh_generation_renderer_integrated
source_work_package=ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf renderer/package concept; adapted for EU/UCITS fresh package generation
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
fresh_generation_renderer_contract_created=true
fresh_generation_renderer_contract=control/ETF_EU_FRESH_GENERATION_RENDERER_INTEGRATION_CONTRACT_V1.md
fresh_generation_package_builder_created=true
fresh_generation_package_builder=tools/build_etf_eu_fresh_generation_package.py
fresh_generation_package_validator_created=true
fresh_generation_package_validator=tools/validate_etf_eu_fresh_generation_package.py
fresh_generation_package_created=true
fresh_generation_package_manifest=output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
fresh_generation_ready_artifact=output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
fresh_generation_dutch_primary_markdown=output/fresh_generation/weekly_etf_eu_review_nl_260710.md
fresh_generation_english_companion_markdown=output/fresh_generation/weekly_etf_eu_review_260710.md
fresh_generation_dutch_primary_html=output/fresh_generation/weekly_etf_eu_review_nl_260710.html
fresh_generation_english_companion_html=output/fresh_generation/weekly_etf_eu_review_260710.html
fresh_generation_dutch_primary_pdf=output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
fresh_generation_english_companion_pdf=output/fresh_generation/weekly_etf_eu_review_260710.pdf
fresh_generation_status=full_package_generated
full_generation_status=renderer_integrated
markdown_output_available=true
html_output_available=true
pdf_output_available=true
ready_for_controlled_delivery=false
fresh_generation_package_validated_by_shell=false
fresh_generation_package_static_contract_satisfied=true
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
readiness_status=fresh_generation_renderer_integrated_ready_for_package_gate
selected_next_package=ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE
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
ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE
```

## ETF-EU-MVP25 objective

Validate the newly generated MVP24 fresh package and decide whether it is ready for controlled delivery preparation.

MVP25 should run or implement a dedicated package-readiness gate over:

```text
output/fresh_generation/weekly_etf_eu_review_nl_260710.md
output/fresh_generation/weekly_etf_eu_review_260710.md
output/fresh_generation/weekly_etf_eu_review_nl_260710.html
output/fresh_generation/weekly_etf_eu_review_260710.html
output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
output/fresh_generation/weekly_etf_eu_review_260710.pdf
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
```

Do not send by default.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md
control/ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1.md
control/ETF_EU_FRESH_GENERATION_RENDERER_INTEGRATION_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP24_FRESH_GENERATION_RENDERER_INTEGRATION_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` package-readiness and delivery-validation patterns before modifying anything:

```text
market-predictions/weekly-etf:tools/validate_etf_delivery_html_contract.py
market-predictions/weekly-etf:tools/validate_etf_pdf_visual_contract.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
market-predictions/weekly-etf:send_report_runtime_html.py
```

## MVP25 recommended scope

```text
1. Validate Dutch-primary / English-companion markdown, HTML and PDF files.
2. Validate no stale delivery wording, no U.S. holdings as EU investable positions, and no authority promotion.
3. Validate manifest and readiness artifact.
4. If all checks pass, update readiness artifact to ready_for_controlled_delivery=true for a later explicit guarded delivery-prep package.
5. Keep delivery separate; no send unless later explicit delivery package authorizes it.
```

## Guardrail

No workflow dispatch, email sending, live delivery, portfolio mutation, valuation-grade promotion, funding authority promotion, or raw Gmail receipt storage should be started from this state update alone.
