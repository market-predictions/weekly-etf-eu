# Decision — ETF-EU-MVP28 Controlled Delivery Execution or Run Queue

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP28_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_DECISION_20260710`

## Decision

Close MVP28 in `decision_only` mode because no explicit run queue or transport execution instruction was supplied.

```text
status=blocked_no_transport_selected
chosen_mode=decision_only
upstream_pattern_adapted=weekly-etf controlled delivery and delivery-manifest concepts; adapted for EU package-bound authority without automatic transport
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
selected_next_package=ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
```

## Upstream basis

MVP28 inspected the closest upstream `weekly-etf` controlled delivery and evidence patterns:

```text
send_report_runtime_html.py
send_report.py
tools/write_etf_delivery_manifest_summary.py
tools/validate_etf_manifest_evidence.py
.github/workflows/send-weekly-report.yml
```

The adapted concepts are pre-send validation, HTML/PDF/package evidence discipline, redacted-recipient delivery manifest discipline, and run-manifest handoff.

## EU adaptation

MVP28 uses the explicit EU authorization artifact and EU package artifacts as authority. It does not use legacy U.S. report discovery, U.S. recipient authority, U.S. delivery authority, U.S. portfolio state, workflow dispatch, or SMTP secrets as EU authority.

## Result

MVP28 creates:

```text
control/ETF_EU_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_CONTRACT_V1.md
tools/prepare_etf_eu_controlled_delivery_execution_or_run_queue.py
tools/validate_etf_eu_controlled_delivery_execution_or_run_queue.py
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
tests/test_etf_eu_controlled_delivery_execution_or_run_queue.py
```

and updates:

```text
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

## Authority rules

MVP28 did not create transport, workflow dispatch, run queue, receipt confirmation, production authority, valuation authority, funding authority, portfolio mutation, recipient exposure, secret exposure, or raw receipt storage.

## Consequence

A future package may choose transport or run queue creation explicitly. The next package is:

```text
ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
```
