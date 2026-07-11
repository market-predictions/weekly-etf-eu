# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING**.

## Latest completion

```text
work_package_id=ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
status=blocked_missing_eu_delivery_workflow_wiring
source_work_package=ETF-EU-MVP28_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf queue-triggered delivery and manifest-evidence concepts; adapted for EU package-bound authority
controlled_delivery_transport_selection_contract=control/ETF_EU_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_CONTRACT_V1.md
controlled_delivery_transport_selection_builder=tools/prepare_etf_eu_controlled_delivery_transport_selection.py
controlled_delivery_transport_selection_validator=tools/validate_etf_eu_controlled_delivery_transport_selection.py
controlled_delivery_transport_selection_artifact=output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json
controlled_delivery_transport_selection_decision=control/decisions/ETF_EU_MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_DECISION_20260710.md
transport_selection_status=blocked_missing_eu_delivery_workflow_wiring
selected_transport_mode=none
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
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
missing_production_component=current-package EU workflow wiring
selected_next_package=ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
```

## Standing upstream-first reuse rule

Before changing ETF EU workflow, runtime, validation, delivery, or control files, inspect the closest upstream `market-predictions/weekly-etf` implementation and record the reuse/adaptation decision.

Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
```

## ETF-EU-MVP28C objective

Wire the EU workflow for the current authorized fresh-package chain.

MVP28B found a specific production blocker: the current EU workflow/runtime path is tied to legacy MVP19/FIX2 delivery package inputs and older queue naming, while the current package chain is MVP25-MVP28.

MVP28C should create or adapt workflow wiring for:

```text
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
control/run_queue/current-package EU queue artifact
```

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_DECISION_20260710.md
```

Then inspect:

```text
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
.github/workflows/send-weekly-report.yml
.github/workflows/send-weekly-etf-eu-report.yml
runtime/send_etf_eu_delivery_package.py
runtime/check_etf_eu_delivery_receipt.py
tools/validate_etf_eu_delivery_evidence.py
```

## MVP28C recommended scope

```text
1. Keep delivery_authorized=true and send_command_allowed=true.
2. Do not re-open authorization.
3. Create current-package workflow wiring.
4. Preserve redaction and evidence boundaries.
5. Do not claim receipt without evidence.
```
