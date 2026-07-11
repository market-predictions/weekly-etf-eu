# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP28F_MANUAL_GUARDED_SEND_WORKFLOW_DISPATCH_REQUIRED**.

## Latest completion

```text
work_package_id=ETF-EU-MVP28F_GUARDED_CURRENT_PACKAGE_SEND_EXECUTION
status=blocked_no_workflow_dispatch_performed
source_work_package=ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf delivery-evidence pattern adapted for EU current-package authority
current_package_send_execution_artifact=output/delivery_control/etf_eu_guarded_current_package_send_execution_20260710_000000.json
current_package_execution_artifact=output/delivery_control/etf_eu_guarded_current_package_execution_20260710_000000.json
dry_run_preflight_result_artifact=output/delivery/etf_eu_current_package_transport_result_20260710_000000_mvp28e_dry_run.json
dry_run_preflight_delivery_evidence_artifact=output/delivery/etf_eu_current_package_delivery_evidence_20260710_000000_mvp28e_dry_run.json
execution_mode=guarded_send
execution_status=blocked_no_workflow_dispatch_performed
delivery_authorized=true
send_command_allowed=true
run_queue_allowed=true
run_queue_created=true
dry_run_supported=true
send_supported_with_guard=true
send_mode_wired=true
workflow_dispatch_allowed=false
workflow_dispatch_performed=false
workflow_run_id=null
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
selected_next_package=ETF-EU-MVP28F_MANUAL_GUARDED_SEND_WORKFLOW_DISPATCH_REQUIRED
```

## Standing upstream-first reuse rule

Before changing ETF EU workflow, runtime, validation, delivery, or control files, inspect the closest upstream `market-predictions/weekly-etf` implementation and record the reuse/adaptation decision.

Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP28F_MANUAL_GUARDED_SEND_WORKFLOW_DISPATCH_REQUIRED
```

## ETF-EU-MVP28F manual dispatch objective

Start the existing current-package workflow outside this connector session, because this session could inspect workflows but could not create a new workflow_dispatch run.

Use:

```text
workflow=.github/workflows/send-weekly-etf-eu-current-package.yml
branch=main
delivery_mode=send
queue_path=control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
send_confirmation=confirm_guarded_send
```

After the run, inspect the committed files:

```text
output/delivery/etf_eu_current_package_transport_result_<runtime_run_id>.json
output/delivery/etf_eu_current_package_delivery_evidence_<runtime_run_id>.json
```

If transport succeeds, move to:

```text
ETF-EU-MVP29_DELIVERY_RUN_MONITOR_AND_RECEIPT_EVIDENCE
```

If transport fails or evidence is missing, move to:

```text
ETF-EU-MVP28G_GUARDED_SEND_FAILURE_REPAIR
```

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP28F_GUARDED_CURRENT_PACKAGE_SEND_EXECUTION_DECISION_20260710.md
```

Then inspect:

```text
.github/workflows/send-weekly-etf-eu-current-package.yml
runtime/send_etf_eu_current_package_delivery.py
tools/validate_etf_eu_current_package_transport_runner.py
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
output/delivery_control/etf_eu_guarded_current_package_send_execution_20260710_000000.json
output/delivery/etf_eu_current_package_transport_result_20260710_000000_mvp28e_dry_run.json
output/delivery/etf_eu_current_package_delivery_evidence_20260710_000000_mvp28e_dry_run.json
```

## MVP28F required boundary

```text
1. Keep delivery_authorized=true and send_command_allowed=true.
2. Do not re-open authorization.
3. Record a real workflow run id before claiming execution.
4. Persist transport result and delivery evidence.
5. Preserve no receipt claim until receipt evidence exists.
```
