# ETF EU MVP10 controlled-send workflow integration or guard replacement v1

## Purpose

MVP10 integrates the MVP09 evidence writer and validator chain into the ETF EU workflow as a guarded validation path.

## Scope

MVP10 adds a fixture validation gate to the workflow after run-bundle creation. MVP10 preserves the existing workflow guard and does not open the protected delivery path.

## Source evidence

```text
source_work_package=ETF-EU-MVP09
delivery_evidence_writer_created=true
delivery_evidence_validator_created=true
run_bundle_delivery_evidence_validator_created=true
delivery_evidence_status=not_attempted
recipient_data_policy=redacted_hash_only
required_languages=nl,en
workflow_send_guard_present=true
workflow_send_guard_removed=false
```

## Integration decision

```text
workflow_integration_type=fixture_validation_gate
guard_replacement_created=false
```

MVP10 chooses integration, not guard replacement.

## Workflow guard rule

The existing workflow send guard remains present, remains before the validation pipeline, and still exits for protected send mode.

## Delivery evidence workflow gate

The workflow now calls:

```text
python tools/validate_etf_eu_delivery_evidence.py --evidence output/delivery/etf_eu_delivery_evidence_20260708_000000.json
```

## Run-bundle evidence workflow gate

The workflow now calls:

```text
python tools/validate_etf_eu_run_bundle_delivery_evidence.py --fixture output/runs/20260708_000000/etf_eu_run_bundle_delivery_evidence_fixture.json
python tools/validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence.py
```

## Protected path rule

MVP10 does not use or unlock the protected delivery path.

## Secret and recipient handling rule

MVP10 does not expose private runtime values or recipient values.

## Failure handling rule

MVP10 must fail closed if the workflow evidence gate is absent, if MVP09 validators are absent, if the guard is removed, if protected mode is unlocked, or if private values are exposed.

## Success claim rule

MVP10 does not claim delivery success. The integrated evidence fixture remains `not_attempted` and `delivery_success=false`.

## What this package may create

```text
workflow evidence validation gate
workflow integration validator
MVP10 artifact
MVP10 notes
MVP10 package validator
MVP10 tests
MVP10 decision record
control-state update
```

## What this package must not execute

```text
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
send_performed=false
delivery_mode_send_unlocked=false
workflow_send_guard_removed=false
delivery_success=false
delivery_success_claimed=false
```

## Next package

```text
ETF-EU-MVP11 — ETF EU workflow dry-run verification with integrated evidence gate
```

## Validation requirements

The MVP10 validator must confirm the workflow evidence gate exists after the run-bundle manifest step, calls the MVP09 evidence validators, preserves the existing guard, does not unlock protected mode, does not claim success, and selects ETF-EU-MVP11.
