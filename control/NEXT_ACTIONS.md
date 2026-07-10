# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION**.

## Latest completion

```text
work_package_id=ETF-EU-MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP
status=completed_guarded_fresh_package_delivery_prep
source_work_package=ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf guarded delivery and delivery-manifest concept; adapted for EU explicit delivery-prep without send authority
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
guarded_fresh_package_delivery_prep_contract_created=true
guarded_fresh_package_delivery_prep_contract=control/ETF_EU_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_CONTRACT_V1.md
guarded_fresh_package_delivery_prep_builder_created=true
guarded_fresh_package_delivery_prep_builder=tools/prepare_etf_eu_guarded_fresh_package_delivery.py
guarded_fresh_package_delivery_prep_validator_created=true
guarded_fresh_package_delivery_prep_validator=tools/validate_etf_eu_guarded_fresh_package_delivery_prep.py
guarded_fresh_package_delivery_prep_created=true
guarded_fresh_package_delivery_prep=output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260710_000000.json
fresh_package_readiness_gate=output/fresh_generation/etf_eu_fresh_package_readiness_gate_20260710_000000.json
fresh_generation_package_manifest=output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
fresh_generation_ready_artifact=output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
ready_for_controlled_delivery=true
delivery_authorized=false
explicit_user_authorization_required=true
guarded_send_confirmation_required=true
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
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
readiness_status=guarded_delivery_prep_created_awaiting_explicit_send_authorization
selected_next_package=ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION
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
ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION
```

## ETF-EU-MVP27 objective

Evaluate whether the user has explicitly authorized a guarded send of the MVP26 delivery-prepped fresh package.

The package is ready for controlled delivery preparation, but delivery is **not authorized** yet:

```text
ready_for_controlled_delivery=true
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

MVP27 should create an explicit guarded-send authorization layer only if the user provides a clear send instruction and the required guarded confirmation phrase. Without that, MVP27 should close or remain blocked with `delivery_authorized=false`.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` explicit guarded-send and delivery-manifest patterns before modifying anything:

```text
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
market-predictions/weekly-etf:tools/write_etf_delivery_manifest_summary.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
```

## MVP27 recommended scope

```text
1. Confirm whether an explicit user send authorization exists.
2. Require a guarded confirmation phrase before setting delivery_authorized=true.
3. If not authorized, keep delivery_authorized=false and do not dispatch anything.
4. If authorized, create a separate authorization artifact only; still keep actual transport as a further controlled step unless explicitly included.
5. Preserve recipient/secrets redaction and transport evidence requirements.
```

## Guardrail

No workflow dispatch, email sending, live delivery, portfolio mutation, valuation-grade promotion, funding authority promotion, production-delivery claim, recipient/secret exposure, raw receipt storage, or receipt confirmation should be started from this state update alone.
