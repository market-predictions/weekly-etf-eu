# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP**.

## Latest completion

```text
work_package_id=ETF-EU-MVP21_POST_DELIVERY_HARDENING
status=completed_post_delivery_hardening
source_work_package=ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf delivery manifest and run manifest closeout pattern; adapted for EU manual Gmail receipt and UCITS authority boundaries
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
workflow_run_id=29105468659
workflow_job_id=86404756891
real_eu_transport_runner=runtime/send_etf_eu_delivery_package.py
manual_receipt_confirmation_artifact=output/delivery/etf_eu_manual_receipt_confirmation_20260710_1755.json
manual_receipt_decision=control/decisions/ETF_EU_MVP20B_GUARDED_RESEND_RECEIPT_DECISION_20260710.md
post_delivery_hardening_decision=control/decisions/ETF_EU_MVP21_POST_DELIVERY_HARDENING_DECISION_20260710.md
delivery_closeout_manifest_created=true
delivery_closeout_manifest_validated=true
delivery_closeout_manifest=output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json
delivery_closeout_manifest_pointer=output/run_manifests/latest_etf_eu_delivery_closeout_manifest_path.txt
existing_client_grade_package_input=ETF-EU-MVP19-FIX2
client_grade_package_ready=true
ready_for_controlled_resend=true
future_guarded_sends_require_persisted_evidence_files=true
raw_receipt_pdf_stored_in_github=false
transport_attempted=true
transport_success=true
resend_performed=true
send_executed=true
delivery_success_closed=true
receipt_confirmed=true
completion_claimed=true
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=post_delivery_hardened
selected_next_package=ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP
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
ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP
```

## ETF-EU-MVP22 objective

Move from one-off controlled resend rescue work to a repeatable weekly EU report operating loop.

The routine loop should define how to generate the next fresh Weekly ETF EU report, validate EU/UCITS pricing/package readiness, send only under explicit guarded authority, persist transport evidence, and close with a deterministic delivery closeout manifest.

Do not regenerate or resend by default from this state update alone.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP21_POST_DELIVERY_HARDENING_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` operating-loop patterns before modifying anything:

```text
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
market-predictions/weekly-etf:tools/write_weekly_etf_run_manifest.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
market-predictions/weekly-etf:runtime/build_etf_report_state.py
market-predictions/weekly-etf:runtime/render_etf_report_from_state.py
```

## MVP22 recommended scope

```text
1. Define the routine weekly EU report runbook from pricing to package to guarded delivery.
2. Decide whether EU should adopt a fresh-run workflow or keep controlled resend separate from generation.
3. Add an EU run manifest equivalent that covers pricing, package, transport evidence, receipt/closeout and authority boundaries.
4. Keep delivery evidence deterministic: no green send without persisted evidence and no receipt claim without receipt proof.
5. Preserve UCITS/EU authority boundaries: valuation_grade=false, funding_authority=false, portfolio_mutation=false, production_delivery_authority=false unless future explicit gates authorize otherwise.
```

## Guardrail

No queue file, workflow dispatch, email sending, transport command, delayed receipt check, report regeneration, or portfolio mutation should be started from this state update alone.
