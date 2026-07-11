# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER**.

## Latest completion

```text
work_package_id=ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
status=completed_current_package_delivery_workflow_wired_validate_dry_run
source_work_package=ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf queue-triggered workflow and evidence concepts; adapted for EU current-package queue validation without automatic live transport
delivery_workflow_wiring_contract=control/ETF_EU_DELIVERY_WORKFLOW_WIRING_CONTRACT_V1.md
current_package_queue_builder=tools/prepare_etf_eu_current_package_delivery_queue.py
current_package_queue_validator=tools/validate_etf_eu_current_package_delivery_queue.py
delivery_workflow_wiring_validator=tools/validate_etf_eu_delivery_workflow_wiring.py
delivery_workflow_wiring_artifact=output/delivery_control/etf_eu_delivery_workflow_wiring_20260710_000000.json
delivery_workflow_wiring_decision=control/decisions/ETF_EU_MVP28C_EU_DELIVERY_WORKFLOW_WIRING_DECISION_20260710.md
workflow_file=.github/workflows/send-weekly-etf-eu-current-package.yml
run_queue_artifact=control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
current_package_chain_supported=true
legacy_mvp19_fix2_only=false
validate_only_supported=true
dry_run_supported=true
send_supported_with_guard=false
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=false
run_queue_allowed=true
run_queue_created=true
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed_from_new_run=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
missing_production_component=current-package live transport runner adapter
selected_next_package=ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
```

## Standing upstream-first reuse rule

Before changing ETF EU workflow, runtime, validation, delivery, or control files, inspect the closest upstream `market-predictions/weekly-etf` implementation and record the reuse/adaptation decision.

Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
```

## ETF-EU-MVP28D objective

Adapt or create the current-package transport runner for the authorized fresh-package chain.

MVP28C created the current-package queue and workflow validation/dry-run entrypoint:

```text
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
.github/workflows/send-weekly-etf-eu-current-package.yml
```

The remaining production component is live current-package transport support. Existing transport runtime is still legacy-package oriented and should be adapted minimally, preserving redaction and receipt-evidence rules.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_DELIVERY_WORKFLOW_WIRING_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP28C_EU_DELIVERY_WORKFLOW_WIRING_DECISION_20260710.md
```

Then inspect:

```text
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
runtime/send_etf_eu_delivery_package.py
runtime/write_etf_eu_delivery_evidence.py
tools/validate_etf_eu_delivery_evidence.py
.github/workflows/send-weekly-etf-eu-current-package.yml
```

## MVP28D recommended scope

```text
1. Keep delivery_authorized=true and send_command_allowed=true.
2. Do not re-open authorization.
3. Add current-package transport runner support.
4. Keep dry-run and send paths separated.
5. Preserve redacted evidence and no receipt claim without evidence.
```
