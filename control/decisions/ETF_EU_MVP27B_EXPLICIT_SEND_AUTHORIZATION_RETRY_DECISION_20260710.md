# Decision — ETF-EU-MVP27B Explicit Authorization Retry

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY_DECISION_20260710`

## Decision

Close MVP27B as authorized for a later controlled delivery step after the user supplied the required standalone guarded confirmation phrase.

```text
status=completed_explicit_guarded_delivery_authorization_created
upstream_pattern_adapted=weekly-etf guarded delivery authorization concept; adapted for EU explicit phrase-gated authority without transport execution
guarded_confirmation_phrase_required=true
guarded_confirmation_phrase_present=true
guarded_confirmation_phrase_matched=true
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
selected_next_package=ETF-EU-MVP28_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE
```

## Basis

MVP27B inspected the live control state and the explicit authorization contract. The current user message supplied the required phrase as standalone authorization text.

## Upstream adaptation

MVP27B keeps the upstream adaptation from `weekly-etf`: borrow guarded delivery, redacted-evidence and run-manifest discipline, but do not port U.S. report discovery, U.S. recipient authority, U.S. secrets, U.S. workflow dispatch, or U.S. transport authority.

## Authorization finding

MVP27B refreshed:

```text
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
```

and set:

```text
authorization_status=authorized_for_future_guarded_delivery_step
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
```

## Authority rules

MVP27B did not create transport, workflow dispatch, run queue, receipt confirmation, production authority, valuation authority, funding authority, portfolio mutation, recipient exposure, secret exposure, or raw receipt storage.

## Consequence

A future controlled delivery package may decide whether to execute a delivery mechanism or create a run queue. The next package is:

```text
ETF-EU-MVP28_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE
```
