# ETF EU MVP09 controlled-send implementation with delivery evidence v1

## Purpose

MVP09 implements the ETF EU delivery evidence writer and validators.

## Scope

MVP09 creates deterministic no-send fixture evidence and validates that the evidence chain can be referenced by a run-bundle fixture. MVP09 does not perform outbound delivery and does not unlock the protected delivery path.

## Source evidence

```text
source_work_package=ETF-EU-MVP08
source_mvp08_artifact=output/client_surface/etf_eu_mvp08_controlled_send_delivery_evidence_contract_20260708_000000.json
recipient_data_policy=redacted_hash_only
required_languages=nl,en
delivery_status_caveat_required=true
final_run_bundle_reference_required=true
evidence_validator_required=true
```

## Rolemodel alignment

MVP09 implements the ETF EU equivalent of the weekly-etf delivery evidence chain: evidence writer, redacted recipient policy, NL/EN language evidence, run-bundle reference, and evidence validator.

## Delivery evidence writer

```text
delivery_evidence_writer_created=true
writer=runtime/write_etf_eu_delivery_evidence.py
```

## Delivery evidence validator

```text
delivery_evidence_validator_created=true
validator=tools/validate_etf_eu_delivery_evidence.py
```

## Run-bundle delivery evidence validator

```text
run_bundle_delivery_evidence_validator_created=true
validator=tools/validate_etf_eu_run_bundle_delivery_evidence.py
```

## Deterministic no-send fixture

```text
delivery_evidence_fixture=output/delivery/etf_eu_delivery_evidence_20260708_000000.json
run_bundle_delivery_evidence_fixture=output/runs/20260708_000000/etf_eu_run_bundle_delivery_evidence_fixture.json
delivery_evidence_status=not_attempted
delivery_success=false
```

## Language evidence semantics

```text
nl = Dutch primary client report
en = English companion report
required_languages=nl,en
```

## Recipient redaction

```text
recipient_data_policy=redacted_hash_only
recipient_plaintext_values_exposed=false
secret_values_exposed=false
```

## Delivery status caveat

Future `smtp_sendmail_returned_no_exception` evidence requires real transport evidence and the caveat that it is not an end-recipient inbox receipt.

## Workflow guard rule

The workflow guard remains present. MVP09 does not unlock the protected delivery path.

## Failure handling

The validator must fail closed without delivery evidence, without success caveat for success status, without redaction, without NL/EN language pair, without run-bundle reference, or on private value exposure.

## Success claim rule

MVP09 does not claim delivery success. The deterministic fixture uses `delivery_success=false`.

## What this package may create

```text
delivery evidence writer
delivery evidence validator
run-bundle delivery evidence validator
deterministic no-send delivery evidence fixture
run-bundle delivery evidence fixture
MVP09 artifact, notes, validator, tests and decision record
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
delivery_success_claimed=false
```

## Next package

```text
ETF-EU-MVP10 — ETF EU controlled-send workflow integration or guard replacement
```

## Validation requirements

The MVP09 validator must confirm the writer, validators and fixtures exist; delivery evidence validates with status not_attempted; run-bundle delivery evidence fixture validates; recipient policy is redacted_hash_only; required languages are nl,en; future success status requires the inbox-receipt caveat; all execution flags remain false; the workflow guard remains present; and selected_next_package=ETF-EU-MVP10.
