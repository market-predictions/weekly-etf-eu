# Decision — ETF-EU-MVP28D Current Package Transport Runner Adapter

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER_DECISION_20260710`

## Decision

Close MVP28D as the current-package transport runner adapter package.

```text
status=completed_current_package_transport_runner_adapter_created
upstream_pattern_adapted=weekly-etf transport and manifest-evidence concepts; adapted for EU current-package queue authority and redacted evidence
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
receipt_confirmed=false
selected_next_package=ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
```

## Upstream basis

MVP28D inspected the upstream `weekly-etf` transport and evidence path:

```text
.github/workflows/send-weekly-report.yml
send_report_runtime_html.py
send_report.py
tools/write_etf_delivery_manifest_summary.py
tools/validate_etf_manifest_evidence.py
```

The adapted concepts are transport execution behind a controlled workflow branch, redacted delivery evidence, artifact persistence, and explicit distinction between transport success and inbox receipt. U.S. report discovery, U.S. recipient authority, U.S. portfolio state and U.S. delivery authority are not EU authority.

## EU adapter result

MVP28D creates:

```text
control/ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1.md
runtime/send_etf_eu_current_package_delivery.py
tools/validate_etf_eu_current_package_transport_runner.py
output/delivery_control/etf_eu_current_package_transport_runner_adapter_20260710_000000.json
tests/test_etf_eu_current_package_transport_runner.py
```

and updates:

```text
.github/workflows/send-weekly-etf-eu-current-package.yml
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

## Boundary

MVP28D did not execute live transport, dispatch a workflow directly, confirm receipt, expose recipients, expose secret values, store raw receipt material, mutate portfolio state, or promote production delivery authority.

## Consequence

The next package may execute a guarded current-package dry-run or guarded send path and then monitor the resulting evidence:

```text
ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
```
