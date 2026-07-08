# ETF EU MVP operator evidence value injection or dry-run execution v1

## Purpose

Resolve the MVP execution fork: inject explicitly supplied non-secret operator values and execute dry-run, or stop with operator action required.

## Scope

MVP04 is the operator evidence value injection or dry-run execution boundary. It is not another abstract authority gate.

## MVP boundary

```text
mvp_series_continued=true
no_more_abstract_gates=true
operator_evidence_required=true
operator_evidence_values_supplied=false
operator_evidence_present=false
operator_evidence_complete=false
operator_evidence_status=operator_values_required
operator_action_required=true
placeholder_values_detected=true
dry_run_preflight_allowed=false
dry_run_preflight_performed=false
delivery_preflight_allowed=false
send_allowed=false
production_delivery=false
selected_next_package=OPERATOR_ACTION_REQUIRED
```

## Source artifacts

MVP04 starts from MVP03 operator evidence completion, MVP02 intake, MVP01 execution readiness, WP15AQ evidence planning, fixed client-grade evidence, and fixed pricing/PDF evidence.

## Operator evidence value inspection

Inspect:

```text
control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md
```

## Operator evidence value injection rule

MVP04 may only replace placeholders with explicitly supplied non-secret references or hashes. It must not invent operator evidence or use fake values.

## Placeholder preservation rule

If operator values are still placeholders, preserve placeholders and stop with OPERATOR_ACTION_REQUIRED.

## Dry-run eligibility rule

Dry-run is eligible only when all required operator evidence values are complete and non-placeholder.

## Dry-run execution rule

No dry-run may execute while operator values are missing or placeholders.

## Dry-run manifest rule

A dry-run manifest may be created only by a real dry-run command that produces a real manifest artifact.

## Send boundary

MVP04 may not send the report.

## Success claim boundary

MVP04 may not claim delivery success without a real dry-run manifest.

## Operator action required rule

If values are still missing, MVP04 must stop with OPERATOR_ACTION_REQUIRED instead of creating another planning package.

## What this package may execute

```text
operator_evidence_value_inspection=true
operator_action_checklist_creation=true
operator_action_required_decision=true
```

## What this package must not execute

```text
value_injection_performed=false
dry_run_preflight_performed=false
send_performed=false
dry_run_manifest_created=false
manifest_created=false
receipt_artifact_created=false
production_manifest_created=false
delivery_success_claimed=false
```

## Next step

```text
OPERATOR_ACTION_REQUIRED — Human operator must supply non-secret evidence references before dry-run execution
```

## Validation requirements

A validator must confirm the value-injection/dry-run document, operator action checklist, artifact, notes, placeholder detection, no-dry-run boundary, no-send boundary, no-success-claim boundary, fixed source evidence, and selected_next_package=OPERATOR_ACTION_REQUIRED. It must fail if selected_next_package starts with ETF-EU-WP15 or ETF-EU-MVP05 while operator_action_required=true.
