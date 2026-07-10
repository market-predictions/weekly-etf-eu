# ETF EU Explicit Guarded Send Authorization Contract V1

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_EXPLICIT_GUARDED_SEND_AUTHORIZATION_CONTRACT_V1`

## Purpose

Define the explicit authorization gate for a guarded send of the MVP26 delivery-prepped fresh Weekly ETF EU package.

MVP27 is an authorization package only. It may create an authorization artifact, but it must not execute transport, dispatch a workflow, create a run queue, expose recipients/secrets, or confirm receipt.

```text
upstream_pattern_adapted=weekly-etf guarded send authorization concept; adapted for EU explicit phrase-gated send authority without transport execution
```

## Scope

MVP27 reviews whether explicit user authorization exists for the readiness-gated and delivery-prepped EU package.

Required package chain:

```text
MVP25 package readiness gate passed
→ MVP26 guarded delivery prep created
→ MVP27 explicit guarded-send authorization review
```

MVP27 must distinguish:

```text
ready_for_controlled_delivery=true
```

from:

```text
delivery_authorized=true
send_executed=true
transport_attempted=true
```

## Authority boundaries

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

Allowed:

```text
decision_allowed=explicit_guarded_send_authorization_review
authorization_artifact_allowed=true
delivery_prep_allowed=false
transport_execution_allowed=false
send_execution_allowed=false
```

Not allowed in MVP27:

```text
send_email=false
workflow_dispatch=false
run_queue_creation=false
transport_attempted=false
receipt_confirmed=false
production_delivery_authority=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
```

## Input package contract

MVP27 may use only the MVP26 delivery-prepped package:

```text
output/fresh_generation/weekly_etf_eu_review_nl_260710.md
output/fresh_generation/weekly_etf_eu_review_260710.md
output/fresh_generation/weekly_etf_eu_review_nl_260710.html
output/fresh_generation/weekly_etf_eu_review_260710.html
output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
output/fresh_generation/weekly_etf_eu_review_260710.pdf
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
output/fresh_generation/etf_eu_fresh_package_readiness_gate_20260710_000000.json
output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260710_000000.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

Rejected as authority:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
weekly_analysis_pro_*.md as EU source truth
U.S. ETF tickers as investable EU holdings
U.S. recipient authority
U.S. delivery authority
legacy weekly-etf sender discovery as EU package authority
```

## Exact confirmation phrase requirement

MVP27 may set `delivery_authorized=true` only when the supplied authorization phrase exactly matches:

```text
AUTHORIZE ETF-EU GUARDED SEND 20260710_000000
```

The phrase must be supplied as an explicit user authorization, not merely as text embedded in the work-package instructions, examples, validation command examples, or contract prose.

If the exact phrase is absent or appears only as an instruction/example, MVP27 must set:

```text
authorization_status=blocked_missing_guarded_confirmation_phrase
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
next_package=ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```

## Authorization artifact contract

The authorization artifact must record:

```text
schema_version=etf_eu_guarded_send_authorization_v1
artifact_type=etf_eu_guarded_send_authorization
ready_for_controlled_delivery=true
explicit_user_authorization_required=true
required_guarded_confirmation_phrase=AUTHORIZE ETF-EU GUARDED SEND 20260710_000000
guarded_confirmation_phrase_present=<true|false>
guarded_confirmation_phrase_matched=<true|false>
delivery_authorized=<true|false>
send_command_allowed=<true|false>
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
```

## Authorized-but-not-sent rules

If the exact phrase is supplied, MVP27 may set:

```text
delivery_authorized=true
send_command_allowed=true
```

but must still keep:

```text
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

Actual transport remains a later explicit package.

## Blocked authorization rules

If the exact phrase is missing, wrong, or only present in instructions/examples, MVP27 must create a blocked authorization artifact and update control state to:

```text
status=blocked_missing_explicit_guarded_send_authorization
delivery_authorized=false
selected_next_package=ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```

## Routine run manifest handoff

The routine run manifest must reference the authorization artifact and preserve transport/receipt flags as false.

## Non-transport guardrails

MVP27 must not:

```text
send email
dispatch workflow
create run queue file
perform live delivery
read or expose SMTP secrets
write plaintext recipient values
mutate portfolio state
promote valuation/funding/portfolio/production authority
confirm receipt for a new run
store raw Gmail PDF in GitHub
treat delivery authorization as transport execution
merge authorization and delivery execution into one implicit workflow
```
