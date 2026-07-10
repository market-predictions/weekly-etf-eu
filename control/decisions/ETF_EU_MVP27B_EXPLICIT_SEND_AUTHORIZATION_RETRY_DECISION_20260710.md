# Decision — ETF-EU-MVP27B Explicit Send Authorization Retry

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY_DECISION_20260710`

## Decision

Close MVP27B as still blocked because the user supplied another instruction brief, not a standalone guarded send authorization.

```text
status=blocked_missing_explicit_guarded_send_authorization
upstream_pattern_adapted=weekly-etf guarded send authorization concept; adapted for EU explicit phrase-gated send authority without transport execution
guarded_confirmation_phrase_required=true
guarded_confirmation_phrase_matched=false
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
selected_next_package=ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```

## Basis

MVP27B inspected the live control state and the prior explicit authorization contract. That contract requires a standalone user authorization phrase and rejects phrase text embedded in instructions, examples, validation commands, or contract prose.

## Upstream adaptation

MVP27B keeps the same upstream adaptation as MVP27: borrow the guarded-send, redacted-evidence and run-manifest discipline from `weekly-etf`, but do not port U.S. report discovery, U.S. recipient authority, U.S. secrets, U.S. workflow dispatch, or U.S. transport authority.

## Authorization finding

The uploaded MVP27B brief again contains the guarded phrase only as instruction/example text. It is not a standalone authorization from the user.

Therefore MVP27B refreshed:

```text
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
```

and kept:

```text
authorization_status=blocked_missing_guarded_confirmation_phrase
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
```

## Authority rules

MVP27B did not create transport, workflow dispatch, run queue, receipt confirmation, production authority, valuation authority, funding authority, portfolio mutation, recipient exposure, secret exposure, or raw receipt storage.

## Consequence

A future authorization retry may proceed only if the user provides the exact guarded phrase as standalone authorization text. Until then, the active package remains:

```text
ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```
