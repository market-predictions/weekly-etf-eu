# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN**.

## Latest completion

```text
work_package_id=ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP
status=completed_routine_weekly_operating_loop_defined
source_work_package=ETF-EU-MVP21_POST_DELIVERY_HARDENING
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf routine workflow and run-manifest pattern; adapted for EU/UCITS authority boundaries
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
routine_operating_loop_contract_created=true
routine_operating_loop_contract=control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md
routine_run_manifest_writer_created=true
routine_run_manifest_writer=tools/write_etf_eu_routine_run_manifest.py
routine_run_manifest_validator_created=true
routine_run_manifest_validator=tools/validate_etf_eu_routine_run_manifest.py
routine_run_manifest_created=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
routine_run_manifest_pointer=output/run_manifests/latest_etf_eu_routine_run_manifest_path.txt
fresh_generation_and_guarded_delivery_kept_separate=true
future_guarded_sends_require_persisted_evidence_files=true
routine_run_manifest_required=true
transport_attempted=false
send_executed=false
receipt_confirmed_from_new_run=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=routine_operating_loop_defined
selected_next_package=ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN
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
ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN
```

## ETF-EU-MVP23 objective

Prove that the routine weekly EU loop can generate a fresh EU report/package dry run from EU state without sending.

MVP23 should use the routine operating-loop contract and run manifest from MVP22, then build a no-send fresh-generation path that can produce current EU/UCITS package/readiness artifacts.

Do not send by default.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP22_ROUTINE_WEEKLY_OPERATING_LOOP_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` fresh-generation patterns before modifying anything:

```text
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
market-predictions/weekly-etf:pricing/run_pricing_pass.py
market-predictions/weekly-etf:runtime/build_etf_report_state.py
market-predictions/weekly-etf:runtime/render_etf_report_from_state.py
market-predictions/weekly-etf:tools/write_weekly_etf_run_manifest.py
```

## MVP23 recommended scope

```text
1. Implement or define a no-send fresh EU report/package generation dry run.
2. Start from EU state and UCITS config, not U.S. portfolio state.
3. Produce Dutch-primary and English-companion package/readiness artifacts if current data allows.
4. Write or update an EU routine run manifest for the dry run.
5. Stop before delivery; guarded send remains a separate explicit workflow-dispatch action.
```

## Guardrail

No workflow dispatch, email sending, live delivery, portfolio mutation, valuation-grade promotion, funding authority promotion, or raw Gmail receipt storage should be started from this state update alone.
