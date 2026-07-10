# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP21_POST_DELIVERY_HARDENING**.

## Latest completion

```text
work_package_id=ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION
status=completed_guarded_resend_with_receipt_confirmed
source_work_package=ETF-EU-MVP20A_REAL_TRANSPORT_LAYER_IMPLEMENTATION
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf redacted delivery-manifest concept; adapted to user-supplied Gmail inbox PDF receipt evidence
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
workflow_run_id=29105468659
workflow_job_id=86404756891
real_eu_transport_runner=runtime/send_etf_eu_delivery_package.py
manual_receipt_confirmation_artifact=output/delivery/etf_eu_manual_receipt_confirmation_20260710_1755.json
manual_receipt_decision=control/decisions/ETF_EU_MVP20B_GUARDED_RESEND_RECEIPT_DECISION_20260710.md
existing_client_grade_package_input=ETF-EU-MVP19-FIX2
client_grade_package_ready=true
ready_for_controlled_resend=true
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
readiness_status=guarded_resend_receipt_confirmed
selected_next_package=ETF-EU-MVP21_POST_DELIVERY_HARDENING
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
ETF-EU-MVP21_POST_DELIVERY_HARDENING
```

## ETF-EU-MVP21 objective

Harden the post-delivery operating loop now that the first controlled resend has been receipt-confirmed.

Do not regenerate or resend the report by default. MVP21 is a post-delivery hardening package.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/work_packages/ETF_EU_MVP20_GUARDED_CONTROLLED_RESEND_INSTRUCTIONS_20260709.md
control/decisions/ETF_EU_MVP20A_REAL_TRANSPORT_LAYER_DECISION_20260710.md
control/decisions/ETF_EU_MVP20B_GUARDED_RESEND_RECEIPT_DECISION_20260710.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
```

Then inspect the closest upstream `weekly-etf` post-delivery/run-manifest pattern before modifying anything:

```text
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
market-predictions/weekly-etf:tools/write_etf_delivery_manifest_summary.py
market-predictions/weekly-etf:tools/write_weekly_etf_run_manifest.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
```

## MVP21 recommended scope

```text
1. Add a first-class EU receipt/manifest validator for manual and workflow receipt evidence.
2. Add a final EU run manifest equivalent to weekly-etf tools/write_weekly_etf_run_manifest.py.
3. Preserve the workflow hardening added after run 29105468659: future guarded sends must persist evidence files or fail.
4. Document the difference between SMTP success, committed transport evidence, and inbox receipt confirmation.
5. Keep valuation_grade=false, funding_authority=false, portfolio_mutation=false, and production_delivery_authority=false unless future explicit gates authorize otherwise.
```

## Guardrail

No queue file, workflow dispatch, email sending, transport command, or delayed receipt check should be started from this state update alone.
