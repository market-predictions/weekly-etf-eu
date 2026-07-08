# ETF EU MVP delivery-preflight evidence acquisition plan v1

## Purpose

Final practical evidence plan before MVP execution.

## Scope

Operator-supplied references only.

## MVP boundary

```text
final_evidence_plan_before_mvp_execution=true
stop_recursive_gating=true
no_more_abstract_gates=true
execution_allowed_now=false
selected_next_package=ETF-EU-MVP01
```

## Evidence required from user/operator

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

## Recipient evidence acquisition

Reference and hash only.

## Transport evidence acquisition

Reference and presence check only.

## Owner approval evidence

Operator approval references only.

## Rollback evidence

Operator rollback references only.

## Validation method

Validate required references and no-delivery boundaries.

## Where evidence is recorded

```text
control/runtime_reference_templates/ETF_EU_MVP_DELIVERY_PREFLIGHT_EVIDENCE_REFERENCE_TEMPLATE.md
```

## What must never be committed

```text
runtime_only_values
plaintext_recipient_values
```

## MVP delivery-preflight handoff

```text
mvp_handoff_created=true
mvp_handoff_status=ready_for_evidence_collection_not_execution
next_package_type=mvp_delivery_preflight_execution
recommended_next_package=ETF-EU-MVP01
fallback_next_package=ETF-EU-WP15AQ-FIX
execution_allowed_now=false
requires_operator_evidence_before_execution=true
```

## Stop rule against further abstract gating

WP15AQ is the final evidence acquisition plan before MVP delivery-preflight execution. After WP15AQ, the next package must be MVP delivery-preflight execution readiness or execution.

## Validation requirements

Validate plan, artifact, notes, handoff, stop rule, fixed source evidence, and no-delivery boundaries.
