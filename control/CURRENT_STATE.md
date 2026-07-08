# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-04

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Current phase

```text
Phase 9 — EU product assembly via donor-port strategy
```

## Core boundary

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
```

## Strategic authority

`weekly-etf-eu` remains the EU/UCITS source-of-truth repo. `weekly-etf` remains a donor for mature implementation patterns only.

```text
Port behavior, not U.S. assumptions.
```

## Closed packages

```text
ETF-EU-WP15V
ETF-EU-WP15W
ETF-EU-WP15X
ETF-EU-WP15Y
ETF-EU-WP15Y-FIX
ETF-EU-WP15Z
ETF-EU-WP15AA
ETF-EU-WP15AA-FIX
ETF-EU-WP15AB
ETF-EU-WP15AC
ETF-EU-WP15AD
ETF-EU-WP15AE
ETF-EU-WP15AF
ETF-EU-WP15AG
ETF-EU-WP15AH
ETF-EU-WP15AI
ETF-EU-WP15AJ
ETF-EU-WP15AK
ETF-EU-WP15AL
ETF-EU-WP15AM
ETF-EU-WP15AN
ETF-EU-WP15AO
ETF-EU-WP15AP
ETF-EU-WP15AQ
ETF-EU-MVP01
ETF-EU-MVP02
ETF-EU-MVP03
ETF-EU-MVP04
ETF-EU-MVP04-FIX
```

## Latest completed package — ETF-EU-MVP04-FIX

```text
repository=market-predictions/weekly-etf-eu
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
secret_values_exposed=false
recipient_plaintext_values_exposed=false
delivery_workflow_alignment_status=rolemodel_gated_safe_default
delivery_execution_status=validate_only_or_dry_run_ready
send_execution_status=blocked_pending_eu_sender_entrypoint_validation
delivery_manifest_framework_exists=true
run_bundle_manifest_framework_exists=true
manual_operator_action_required_status=superseded_by_workflow_alignment
operator_action_required=false
selected_next_package=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN
selected_next_package_title=Run ETF EU workflow with delivery_mode validate_only first, then dry_run if green
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

## MVP04-FIX delivery alignment answer

```text
Do I need to fill the operator evidence reference template? No. MVP04-FIX supersedes that manual route. ETF EU delivery now follows the weekly-etf rolemodel direction: workflow_dispatch delivery_mode, GitHub secret names declared in the workflow, delivery manifest framework, run bundle framework, and no delivery-success claim without manifest evidence. The next step is to run the ETF EU workflow with delivery_mode=validate_only, then delivery_mode=dry_run if validate_only is green. delivery_mode=send remains blocked until an EU-specific sender entrypoint is validated.
```

## Active product roadmap

```text
RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN — run ETF EU workflow with delivery_mode=validate_only, then dry_run if green
```

## Immediate next action

In GitHub Actions, run:

```text
Weekly ETF EU UCITS rolemodel delivery workflow
```

First with:

```text
delivery_mode=validate_only
```

If green, run again with:

```text
delivery_mode=dry_run
```

Do not use `delivery_mode=send` until an EU-specific sender entrypoint has been explicitly validated.
