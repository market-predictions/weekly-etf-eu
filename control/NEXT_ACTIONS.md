# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP28F_GUARDED_CURRENT_PACKAGE_SEND_EXECUTION**.

## Latest completion

```text
work_package_id=ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
status=completed_current_package_dry_run_execution
source_work_package=ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf guarded transport execution and manifest-evidence concepts; adapted for EU current-package dry-run evidence
current_package_execution_artifact=output/delivery_control/etf_eu_guarded_current_package_execution_20260710_000000.json
transport_result_artifact=output/delivery/etf_eu_current_package_transport_result_20260710_000000_mvp28e_dry_run.json
delivery_evidence_artifact=output/delivery/etf_eu_current_package_delivery_evidence_20260710_000000_mvp28e_dry_run.json
execution_mode=dry_run
delivery_authorized=true
send_command_allowed=true
run_queue_allowed=true
run_queue_created=true
dry_run_supported=true
send_supported_with_guard=true
send_mode_wired=true
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
selected_next_package=ETF-EU-MVP28F_GUARDED_CURRENT_PACKAGE_SEND_EXECUTION
```

## Standing upstream-first reuse rule

Before changing ETF EU workflow, runtime, validation, delivery, or control files, inspect the closest upstream `market-predictions/weekly-etf` implementation and record the reuse/adaptation decision.

Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP28F_GUARDED_CURRENT_PACKAGE_SEND_EXECUTION
```

## ETF-EU-MVP28F objective

Execute the guarded current-package send path only if explicitly selected.

MVP28E completed dry-run evidence for:

```text
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
runtime/send_etf_eu_current_package_delivery.py
output/delivery/etf_eu_current_package_transport_result_20260710_000000_mvp28e_dry_run.json
output/delivery/etf_eu_current_package_delivery_evidence_20260710_000000_mvp28e_dry_run.json
```

MVP28F should use the workflow branch:

```text
.github/workflows/send-weekly-etf-eu-current-package.yml
```

with explicit guarded send selection only. It must preserve redacted evidence and must not claim receipt without receipt evidence.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION_DECISION_20260710.md
```

Then inspect:

```text
.github/workflows/send-weekly-etf-eu-current-package.yml
runtime/send_etf_eu_current_package_delivery.py
tools/validate_etf_eu_current_package_transport_runner.py
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
output/delivery_control/etf_eu_guarded_current_package_execution_20260710_000000.json
output/delivery/etf_eu_current_package_transport_result_20260710_000000_mvp28e_dry_run.json
output/delivery/etf_eu_current_package_delivery_evidence_20260710_000000_mvp28e_dry_run.json
```

## MVP28F recommended scope

```text
1. Keep delivery_authorized=true and send_command_allowed=true.
2. Do not re-open authorization.
3. Execute guarded send only with explicit selection.
4. Persist transport result and delivery evidence.
5. Preserve no receipt claim until receipt evidence exists.
```
