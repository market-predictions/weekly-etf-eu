# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION**.

## Latest completion

```text
work_package_id=ETF-EU-MVP28_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE
status=blocked_no_transport_selected
source_work_package=ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf controlled delivery and delivery-manifest concepts; adapted for EU package-bound authority without automatic transport
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
controlled_delivery_contract=control/ETF_EU_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_CONTRACT_V1.md
controlled_delivery_builder=tools/prepare_etf_eu_controlled_delivery_execution_or_run_queue.py
controlled_delivery_validator=tools/validate_etf_eu_controlled_delivery_execution_or_run_queue.py
controlled_delivery_decision_artifact=output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
controlled_delivery_decision_status=blocked_no_transport_selected
chosen_mode=decision_only
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=false
run_queue_allowed=false
run_queue_created=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed_from_new_run=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
generation_and_delivery_separate=true
readiness_status=controlled_delivery_decision_blocked_no_transport_selected_awaiting_transport_selection
selected_next_package=ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
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
ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
```

## ETF-EU-MVP28B objective

Select an explicit controlled delivery mechanism for the authorized EU fresh package.

The package is authorized and has a controlled delivery decision artifact, but no queue or transport has been created:

```text
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
controlled_delivery_decision_status=blocked_no_transport_selected
workflow_dispatch_allowed=false
run_queue_allowed=false
run_queue_created=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

MVP28B may create a run queue artifact or a further blocked transport-selection artifact. It must not claim delivery success or receipt unless real evidence exists.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP28_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` controlled delivery and delivery-manifest patterns before modifying anything:

```text
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
market-predictions/weekly-etf:tools/write_etf_delivery_manifest_summary.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
```

## MVP28B recommended scope

```text
1. Confirm delivery_authorized=true and send_command_allowed=true.
2. Confirm MVP28 selected decision_only/no-transport.
3. Require explicit selection before creating a run queue or transport execution.
4. Preserve recipient/secrets redaction.
5. Do not claim receipt without delivery manifest evidence.
```

## Guardrail

No workflow dispatch, live delivery, portfolio mutation, valuation-grade promotion, funding authority promotion, production-delivery claim, recipient/secret exposure, raw receipt storage, or receipt confirmation should be started without explicit controlled-delivery evidence.
