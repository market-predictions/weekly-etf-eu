# Decision — ETF-EU-MVP28C EU Delivery Workflow Wiring

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP28C_EU_DELIVERY_WORKFLOW_WIRING_DECISION_20260710`

## Decision

Close MVP28C as current-package workflow wiring created for validation and dry-run evidence, with live current-package transport left to a later explicit adapter package.

```text
status=completed_current_package_delivery_workflow_wired_validate_dry_run
upstream_pattern_adapted=weekly-etf queue-triggered workflow and evidence concepts; adapted for EU current-package queue validation without automatic live transport
delivery_authorized=true
send_command_allowed=true
current_package_chain_supported=true
run_queue_allowed=true
run_queue_created=true
workflow_dispatch_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
selected_next_package=ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
```

## Upstream basis

MVP28C inspected the upstream `weekly-etf` queue-triggered workflow and evidence model:

```text
.github/workflows/send-weekly-report.yml
send_report_runtime_html.py
send_report.py
tools/write_etf_delivery_manifest_summary.py
tools/validate_etf_manifest_evidence.py
```

The adapted concepts are queue-triggered execution, pre-send validation, redacted evidence, artifact persistence, and run-manifest closeout. U.S. portfolio state, U.S. report discovery, U.S. recipient authority and U.S. delivery authority are not EU authority.

## EU wiring result

MVP28C created a separate current-package workflow entrypoint:

```text
.github/workflows/send-weekly-etf-eu-current-package.yml
```

It consumes:

```text
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
```

and validates the current MVP25-MVP28 package chain:

```text
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json
```

## Boundary

MVP28C did not execute live transport, dispatch a workflow directly, confirm receipt, expose recipients, expose secret values, store raw receipt material, mutate portfolio state, or promote production delivery authority.

## Consequence

The next package should adapt or create the current-package transport runner for live guarded execution:

```text
ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
```
