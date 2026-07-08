# ETF EU MVP operator evidence intake and dry-run v1

## Purpose

Create the practical operator evidence intake surface needed before ETF EU delivery-preflight dry-run execution.

## Scope

MVP02 continues the MVP execution series and is not another abstract authority gate.

## MVP boundary

```text
mvp_series_continued=true
no_more_abstract_gates=true
operator_evidence_required=true
operator_evidence_present=false
operator_evidence_complete=false
operator_evidence_status=missing_required_for_dry_run
dry_run_preflight_allowed=false
dry_run_preflight_performed=false
delivery_preflight_allowed=false
send_allowed=false
production_delivery=false
```

## Source artifacts

MVP02 starts from MVP01 execution readiness, WP15AQ evidence acquisition planning, fixed client-grade evidence, and fixed pricing/PDF evidence.

## Operator evidence intake fields

```text
recipient_set_reference_id
recipient_set_hash
recipient_owner_approval_reference
recipient_rollback_reference
transport_reference_id
transport_presence_check_reference
transport_owner_approval_reference
transport_rollback_reference
explicit_mvp_preflight_authority_reference
```

## Operator evidence reference template

```text
control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md
```

The template contains placeholders only.

## Evidence validation rule

Dry-run eligibility requires all operator evidence reference fields to be present as non-runtime committed references or hashes.

## Dry-run eligibility rule

If any required operator evidence reference is missing, dry-run is not eligible and must not execute.

## Dry-run execution boundary

```text
dry_run_preflight_prepared=true
dry_run_preflight_performed=false
delivery_preflight_performed=false
send_performed=false
dry_run_manifest_created=false
manifest_created=false
```

## Send boundary

MVP02 may not send the report.

## Manifest and receipt rule

MVP02 may not claim delivery success without a real manifest or receipt.

## What this package may create

```text
operator_evidence_intake_surface=true
operator_evidence_reference_template=true
dry_run_readiness_decision=true
```

## What this package must not create

```text
dry_run_preflight_performed=false
send_performed=false
dry_run_manifest_created=false
manifest_created=false
receipt_artifact_created=false
production_manifest_created=false
delivery_success_claimed=false
```

## Next MVP step

```text
ETF-EU-MVP03 — ETF EU operator evidence completion and preflight dry-run execution
```

## Validation requirements

A validator must confirm the intake document, reference template, artifact, notes, missing-evidence branch, no-send boundary, no-success-claim boundary, fixed source evidence, and selected_next_package=ETF-EU-MVP03. It must fail if selected_next_package starts with ETF-EU-WP15.
