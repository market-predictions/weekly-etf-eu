# ETF EU Controlled Delivery Transport Selection Contract V1

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_CONTRACT_V1`

## Purpose

Define the transport-selection layer for the authorized Weekly ETF EU fresh package.

MVP28B is not another authorization package. The current package has:

```text
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
```

MVP28B must choose whether the repository has compatible EU workflow wiring for the current fresh package chain.

```text
upstream_pattern_adapted=weekly-etf queue-triggered delivery and manifest-evidence concepts; adapted for EU package-bound authority
```

## Authority boundaries

MVP28B may create a transport-selection artifact and may create a queue artifact only when a compatible EU workflow can consume it.

MVP28B must not re-open authorization, mutate portfolio state, expose recipient values, expose secret values, store raw receipt material, or claim delivery success without evidence.

## Current package chain

MVP28B must use the current package chain:

```text
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260710_000000.json
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

Legacy MVP19/FIX2 delivery package artifacts are not authority for this MVP28B package.

## Transport-selection artifact contract

The artifact must record:

```text
schema_version=etf_eu_controlled_delivery_transport_selection_v1
artifact_type=etf_eu_controlled_delivery_transport_selection
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
controlled_delivery_decision_status=blocked_no_transport_selected
transport_selection_status=<controlled_delivery_run_queue_created|blocked_missing_eu_delivery_workflow_wiring>
selected_transport_mode=<run_queue|none>
run_queue_created=<true|false>
run_queue_allowed=<true|false>
workflow_dispatch_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
```

## Queue compatibility rule

A queue artifact may be created only if an EU workflow consumes that exact queue path and is wired to the current fresh package artifacts.

If the only available EU workflow targets legacy MVP19/FIX2 package inputs, MVP28B must record:

```text
transport_selection_status=blocked_missing_eu_delivery_workflow_wiring
selected_transport_mode=none
run_queue_created=false
run_queue_allowed=false
workflow_dispatch_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
next_package=ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING
```

## Evidence rule

Delivery success and receipt confirmation require explicit evidence artifacts. They must remain false in a wiring-gap decision.
