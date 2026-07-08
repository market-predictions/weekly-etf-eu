# Weekly ETF EU Review OS — Next Actions

Current priority: **RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN — run ETF EU workflow with delivery_mode=validate_only, then dry_run if green**.

## Latest completion

```text
work_package_id=ETF-EU-MVP04-FIX
status=completed_rolemodel_delivery_alignment
source_work_package=ETF-EU-MVP04
manual_evidence_route_superseded=true
operator_reference_template_required_for_delivery=false
operator_hash_requirement_removed=true
workflow_delivery_mode_input_created=true
delivery_mode_default=validate_only
delivery_mode_options=validate_only,dry_run,send
push_delivery_mode=validate_only
dry_run_mode_declared=true
send_mode_declared=true
send_mode_blocked_until_eu_sender_validated=true
rolemodel_secret_names_declared=true
private_values_exposed=false
recipient_values_exposed=false
delivery_workflow_alignment_status=rolemodel_gated_safe_default
delivery_execution_status=validate_only_or_dry_run_ready
send_execution_status=blocked_pending_eu_sender_entrypoint_validation
delivery_manifest_framework_exists=true
run_bundle_manifest_framework_exists=true
manual_operator_action_required_status=superseded_by_workflow_alignment
operator_action_required=false
selected_next_package=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN
selected_next_package_is_mvp05=false
selected_next_package_is_wp15=false
production_delivery=false
send_performed=false
email_delivery=false
delivery_success_claimed=false
delivery_success_claim_allowed=false
manifest_required_for_success_claim=true
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
pricing_evidence_changed=false
source_pdf_replaced=false
new_pdf_created=false
renderer_changed=false
```

## Active next step

```text
RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN — run ETF EU workflow with delivery_mode=validate_only, then dry_run if green
```

Purpose:

```text
Use the existing ETF EU workflow and delivery manifest framework in the weekly-etf rolemodel style. Do not fill manual operator evidence templates. Do not open ETF-EU-MVP05 merely to continue the prior manual route. Do not return to WP15 authority gates.
```

## Operator instructions

In GitHub Actions, run:

```text
Weekly ETF EU UCITS rolemodel delivery workflow
```

First choose:

```text
delivery_mode=validate_only
```

If that workflow is green, run again with:

```text
delivery_mode=dry_run
```

Do not choose:

```text
delivery_mode=send
```

until an EU-specific sender entrypoint has been explicitly validated.

## Scope guardrails

```text
Do not fill manual operator evidence/hash reference templates for delivery.
Do not open ETF-EU-MVP05 merely to ask for the same values again.
Do not return to WP15 abstract authority gates unless a concrete validator failure occurs.
Do not fetch new close prices outside the workflow run.
Do not mutate portfolio state.
Do not create valuation-grade authority.
Do not create funding authority.
Do not create funded positions.
Do not change recommendation logic in production.
Do not claim delivery success without a real delivery manifest or receipt.
Do not expose private runtime values.
Do not expose recipient values.
```
