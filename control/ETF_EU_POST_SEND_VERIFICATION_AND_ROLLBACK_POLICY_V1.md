# ETF EU post-send verification and rollback policy v1

## Purpose

Define post-send verification and rollback requirements for future ETF EU report delivery packages.

## Scope

This policy defines verification and rollback requirements only. It does not verify a delivery that has not occurred.

## Post-send verification loop

A future verification loop must require real delivery evidence before any success claim.

```text
verification_allowed=false
receipt_required_before_success_claim=true
success_claim_rule=no_success_claim_without_receipt_or_manifest
```

## Receipt evidence requirements

A future receipt must include transport, recipient set reference, message or transport receipt, send timestamp, send result, verification timestamp, verification result, and failure reason when applicable.

This policy does not create a delivery receipt.

## Manifest evidence requirements

A future manifest must identify the exact run, commit, workflow, source report/PDF, recipient set, transport reference, send timestamp, delivery status, receipt path, verification status, and rollback status.

This policy does not create a production manifest.

## Failure handling

If any required gate or evidence item is missing, the future delivery package must abort before send and report the missing gate.

## Rollback and abort policy

```text
policy_status=defined_not_executable
abort_conditions_defined=true
rollback_allowed=false
failure_state=abort_before_send_if_any_gate_missing
```

## Delayed delivery confirmation policy

Delayed confirmation may only be executed by a later delivery package that created real send evidence. No success may be claimed without receipt or manifest evidence.

## What this policy does not authorize

```text
send_report=false
create_delivery_receipt=false
create_production_manifest=false
verify_nonexistent_delivery=false
authorize_delayed_delivery_checks=false
```

A later delivery package must create real delivery evidence before any delivery success may be claimed.

## Validation requirements

A validator must confirm that the policy exists, required sections are present, verification remains false, rollback execution remains false, and no delivery success is claimed.
