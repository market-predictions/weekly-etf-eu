# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION**.

## Latest completion

```text
work_package_id=ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
status=completed_current_package_transport_runner_adapter_created
source_work_package=ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf transport and manifest-evidence concepts; adapted for EU current-package queue authority and redacted evidence
current_package_transport_runner_contract=control/ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1.md
current_package_transport_runner=runtime/send_etf_eu_current_package_delivery.py
current_package_transport_validator=tools/validate_etf_eu_current_package_transport_runner.py
current_package_transport_runner_adapter_artifact=output/delivery_control/etf_eu_current_package_transport_runner_adapter_20260710_000000.json
current_package_transport_runner_decision=control/decisions/ETF_EU_MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER_DECISION_20260710.md
workflow_file=.github/workflows/send-weekly-etf-eu-current-package.yml
run_queue_artifact=control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
current_package_chain_supported=true
transport_runner_adapter_created=true
dry_run_supported=true
send_supported_with_guard=true
send_mode_wired=true
delivery_authorized=true
send_command_allowed=true
run_queue_allowed=true
run_queue_created=true
workflow_dispatch_allowed=false
transport_execution_allowed=false
live_transport_executed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed_from_new_run=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
selected_next_package=ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
```

## Standing upstream-first reuse rule

Before changing ETF EU workflow, runtime, validation, delivery, or control files, inspect the closest upstream `market-predictions/weekly-etf` implementation and record the reuse/adaptation decision.

Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
```

## ETF-EU-MVP28E objective

Execute the guarded current-package dry-run or guarded send path using the current-package runner and workflow wiring created in MVP28D.

MVP28D created:

```text
runtime/send_etf_eu_current_package_delivery.py
tools/validate_etf_eu_current_package_transport_runner.py
.github/workflows/send-weekly-etf-eu-current-package.yml
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
```

MVP28E should choose one explicit execution mode:

```text
dry_run first is recommended
send only if explicitly selected through the guarded workflow input
```

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER_DECISION_20260710.md
```

Then inspect:

```text
.github/workflows/send-weekly-etf-eu-current-package.yml
runtime/send_etf_eu_current_package_delivery.py
tools/validate_etf_eu_current_package_transport_runner.py
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
output/delivery_control/etf_eu_current_package_transport_runner_adapter_20260710_000000.json
```

## MVP28E recommended scope

```text
1. Keep delivery_authorized=true and send_command_allowed=true.
2. Do not re-open authorization.
3. Execute dry_run first unless user explicitly selects guarded send.
4. Persist result and evidence artifacts.
5. Preserve redacted evidence and no receipt claim without evidence.
```
