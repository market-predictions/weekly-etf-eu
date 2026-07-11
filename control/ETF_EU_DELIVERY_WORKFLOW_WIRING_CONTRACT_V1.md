# ETF EU Delivery Workflow Wiring Contract V1

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_DELIVERY_WORKFLOW_WIRING_CONTRACT_V1`

## Purpose

Define current-package workflow wiring for the authorized Weekly ETF EU fresh package chain.

This contract is production-path wiring. It must not re-open authorization or mutate portfolio state.

```text
upstream_pattern_adapted=weekly-etf queue-triggered workflow and evidence concepts; adapted for EU current-package queue validation without automatic live transport
```

## Current package authority

The authorized current package chain is:

```text
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json
output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

Required authority flags:

```text
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
```

## Queue artifact contract

The current-package queue artifact path is:

```text
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
```

The queue artifact may reference package, authorization, decision, transport-selection and routine manifest paths. It must not contain recipient plaintext, provider credentials, mailbox contents, or raw receipt material.

## Workflow wiring contract

The current-package workflow wiring must:

```text
listen_for_current_package_queue=true
support_validate_only=true
support_dry_run_evidence=true
preserve_guarded_live_transport_boundary=true
legacy_mvp19_fix2_only=false
```

The wiring must not:

```text
claim_transport_success_without_evidence=true
confirm_receipt_without_evidence=true
expose_recipient_plaintext=true
expose_secret_values=true
store_raw_receipt_material=true
mutate_portfolio_state=true
```

## Evidence policy

Validation and dry-run evidence may be produced without outbound transport. Live transport evidence and receipt evidence require a later explicit execution package and real artifacts.

## Handoff

If current-package queue and workflow validation are wired but live current-package transport is not executed, the next package is:

```text
ETF-EU-MVP28D_CURRENT_PACKAGE_TRANSPORT_RUNNER_ADAPTER
```
