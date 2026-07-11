# Decision — ETF-EU-MVP28B Controlled Delivery Transport Selection

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_DECISION_20260710`

## Decision

Close MVP28B as blocked on missing EU delivery workflow wiring for the current fresh package chain.

```text
status=blocked_missing_eu_delivery_workflow_wiring
selected_transport_mode=none
upstream_pattern_adapted=weekly-etf queue-triggered delivery and manifest-evidence concepts; adapted for EU package-bound authority
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=false
run_queue_allowed=false
run_queue_created=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
selected_next_package=ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
```

## Upstream basis

MVP28B inspected the upstream `weekly-etf` queue-triggered production path and evidence model:

```text
.github/workflows/send-weekly-report.yml
send_report_runtime_html.py
send_report.py
tools/write_etf_delivery_manifest_summary.py
tools/validate_etf_manifest_evidence.py
```

The adapted concepts are queue-triggered delivery, pre-send validation, redacted delivery evidence, and run-manifest closeout.

## EU workflow finding

The EU repo has two relevant workflow facts:

```text
.github/workflows/send-weekly-report.yml disables the inherited U.S. sender.
.github/workflows/send-weekly-etf-eu-report.yml exists, but it is wired to legacy MVP19/FIX2 delivery package inputs and the older queue pattern.
```

The current MVP28B package chain is the MVP25-MVP28 fresh package chain:

```text
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
```

No compatible queue consumer was found for:

```text
control/run_queue/etf_eu_controlled_delivery_request_20260710_000000.md
```

Therefore MVP28B did not create a queue artifact.

## Result

MVP28B creates:

```text
control/ETF_EU_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_CONTRACT_V1.md
tools/prepare_etf_eu_controlled_delivery_transport_selection.py
tools/validate_etf_eu_controlled_delivery_transport_selection.py
output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json
tests/test_etf_eu_controlled_delivery_transport_selection.py
```

and updates:

```text
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

## Authority rules

MVP28B did not create a queue, dispatch a workflow, execute transport, confirm receipt, expose recipients, expose secrets, store raw receipt material, mutate portfolio state, or promote production delivery authority.

## Consequence

The next production-path package is:

```text
ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
```

MVP28C should wire the EU workflow to consume the current fresh-package chain and a current-package queue artifact without using legacy MVP19/FIX2 package assumptions.
