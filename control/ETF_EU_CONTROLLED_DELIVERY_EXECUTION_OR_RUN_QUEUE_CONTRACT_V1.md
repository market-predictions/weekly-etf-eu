# ETF EU Controlled Delivery Execution or Run Queue Contract V1

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_CONTRACT_V1`

## Purpose

Define the controlled delivery decision layer for the authorized Weekly ETF EU fresh package.

MVP28 is an operational decision package. It may create a controlled delivery decision artifact and, if separately selected, a non-secret EU run-queue artifact. It must not silently collapse authorization into transport.

```text
upstream_pattern_adapted=weekly-etf controlled delivery and delivery-manifest concepts; adapted for EU package-bound authority without automatic transport
```

## Scope

MVP28 starts from an authorized but not transported package:

```text
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
```

MVP28 may close with one of:

```text
controlled_delivery_decision_status=blocked_no_transport_selected
controlled_delivery_decision_status=run_queue_artifact_created
controlled_delivery_decision_status=transport_execution_recorded
```

Default is `blocked_no_transport_selected` unless the user explicitly selects a run queue or transport execution.

## Authority boundaries

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

Allowed:

```text
decision_allowed=controlled_delivery_execution_or_run_queue_decision
delivery_authorized_required=true
send_command_allowed_required=true
controlled_delivery_artifact_allowed=true
run_queue_artifact_allowed=true_if_explicitly_selected
transport_execution_allowed=true_only_with_real_transport_evidence
```

Not allowed without real evidence:

```text
transport_success=true
receipt_confirmed=true
delivery_success_claim=true
production_delivery_claim=true
```

Never allowed in MVP28:

```text
valuation_grade_promotion=true
funding_authority_promotion=true
portfolio_mutation=true
recipient_plaintext_values_exposed=true
secret_values_exposed=true
raw_receipt_pdf_stored_in_github=true
```

## Input package contract

MVP28 must use only the authorized EU package chain:

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
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

Rejected as EU authority:

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
plaintext recipient values
SMTP secrets
raw Gmail receipt PDFs
```

## Delivery decision artifact contract

The controlled delivery decision artifact must record:

```text
schema_version=etf_eu_controlled_delivery_decision_v1
artifact_type=etf_eu_controlled_delivery_decision
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
controlled_delivery_decision_status=<blocked_no_transport_selected|run_queue_artifact_created|transport_execution_recorded>
workflow_dispatch_allowed=false unless explicit workflow evidence exists
run_queue_allowed=<true only for explicit run_queue mode>
run_queue_created=<true only for explicit run_queue mode>
transport_execution_allowed=false unless explicit transport evidence exists
send_executed=false unless transport actually happened
transport_attempted=false unless transport actually happened
transport_success=false unless delivery manifest evidence proves it
receipt_confirmed=false unless actual receipt evidence exists
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
```

## Run queue artifact contract

If a run queue artifact is created, it must live under the EU-controlled queue path:

```text
control/run_queue/etf_eu_controlled_delivery_request_20260710_000000.md
```

The queue artifact must not include plaintext recipients, SMTP secrets, raw receipt material, or U.S. delivery authority. It may reference package artifact paths and the authorization artifact.

## Delivery evidence policy

Delivery success may be recorded only with delivery manifest evidence. SMTP return without exception is not an end-recipient inbox receipt. Receipt confirmation requires separate receipt evidence.

## Routine run manifest handoff

The routine run manifest must reference the controlled delivery decision artifact and preserve all transport and receipt flags as false for `decision_only`.

## Blocked no-transport rules

When no explicit run queue or transport execution instruction exists, MVP28 must choose:

```text
controlled_delivery_decision_status=blocked_no_transport_selected
workflow_dispatch_allowed=false
run_queue_allowed=false
run_queue_created=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
next_package=ETF-EU-MVP28B_CONTROLLED_DELIVERY_TRANSPORT_SELECTION
```
