# Decision — ETF-EU-MVP27 Explicit Guarded Send Authorization

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION_DECISION_20260710`

## Decision

Close MVP27 as blocked because the user did not provide a standalone exact guarded confirmation phrase.

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

## Upstream basis

MVP27 inspected the closest upstream `weekly-etf` guarded-send, delivery-manifest and workflow patterns:

```text
send_report_runtime_html.py
send_report.py
tools/write_etf_delivery_manifest_summary.py
tools/validate_etf_manifest_evidence.py
.github/workflows/send-weekly-report.yml
```

The adapted concepts are pre-send guard separation, explicit delivery evidence discipline, redacted-recipient manifest discipline, run-manifest handoff, and the rule that delivery success may not be claimed without delivery evidence.

## EU adaptation

The EU authorization layer validates explicit EU package artifacts and MVP26 delivery-prep state. It does not use legacy U.S. report discovery, U.S. recipient authority, U.S. delivery authority, U.S. portfolio state, or U.S. workflow assumptions as EU authority.

## Authorization finding

The guarded confirmation phrase appeared only inside the uploaded MVP27 task brief as an instruction/example, not as a standalone user authorization.

Therefore MVP27 created this blocked authorization artifact:

```text
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
```

The artifact keeps:

```text
authorization_status=blocked_missing_guarded_confirmation_phrase
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
```

## Authority rules

MVP27 did not create transport, workflow dispatch, run queue, receipt confirmation, production authority, valuation authority, funding authority, portfolio mutation, recipient exposure, secret exposure, or raw receipt storage.

## Consequence

A future attempt may retry authorization only if the user provides the exact standalone guarded phrase. The next package is:

```text
ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```
