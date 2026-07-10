# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY**.

## Latest completion

```text
work_package_id=ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
status=blocked_missing_explicit_guarded_send_authorization
source_work_package=ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf guarded send authorization concept; adapted for EU explicit phrase-gated send authority without transport execution
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
explicit_guarded_send_authorization_artifact=output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
explicit_guarded_send_authorization_retry_decision=control/decisions/ETF_EU_MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY_DECISION_20260710.md
guarded_confirmation_phrase_required=true
guarded_confirmation_phrase_present=false
guarded_confirmation_phrase_matched=false
authorization_status=blocked_missing_guarded_confirmation_phrase
ready_for_controlled_delivery=true
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed_from_new_run=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
generation_and_delivery_separate=true
readiness_status=explicit_guarded_send_authorization_retry_blocked_awaiting_exact_standalone_confirmation_phrase
selected_next_package=ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```

## Standing upstream-first reuse rule

Before creating or materially changing any ETF EU task, work package, workflow, runtime script, validator, renderer, delivery step, or control file, first inspect the closest upstream `market-predictions/weekly-etf` implementation.

Record one of:

```text
upstream_pattern_reused=<file or concept>
upstream_pattern_adapted=<file or concept + reason>
upstream_pattern_rejected=<file or concept + EU authority reason>
no_upstream_equivalent_found=<search terms / inspected files>
```

Borrow mature concepts and safeguards. Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY
```

## ETF-EU-MVP27B objective

Retry explicit guarded-send authorization only if the user provides the exact standalone guarded confirmation phrase.

The package is ready for controlled delivery preparation, but delivery is **not authorized** yet:

```text
ready_for_controlled_delivery=true
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
transport_execution_allowed=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

MVP27B may set `delivery_authorized=true` only if the user provides the exact standalone guarded confirmation phrase required by `control/ETF_EU_EXPLICIT_GUARDED_SEND_AUTHORIZATION_CONTRACT_V1.md`. Text embedded in task instructions, code blocks, examples, or validation command examples is not sufficient.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_EXPLICIT_GUARDED_SEND_AUTHORIZATION_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` explicit guarded-send and delivery-manifest patterns before modifying anything:

```text
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
market-predictions/weekly-etf:tools/write_etf_delivery_manifest_summary.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
```

## MVP27B recommended scope

```text
1. Confirm whether the exact standalone guarded confirmation phrase is present in the user instruction.
2. If absent, keep delivery_authorized=false and do not dispatch anything.
3. If present, update authorization artifact only.
4. Keep actual transport as a later explicit controlled-send package.
5. Preserve recipient/secrets redaction and transport evidence requirements.
```

## Guardrail

No workflow dispatch, email sending, live delivery, run queue creation, portfolio mutation, valuation-grade promotion, funding authority promotion, production-delivery claim, recipient/secret exposure, raw receipt storage, or receipt confirmation should be started from this state update alone.
