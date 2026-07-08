# ETF EU MVP08 controlled-send delivery evidence contract v1

## Purpose

MVP08 defines the ETF EU controlled-send delivery evidence contract.

## Scope

MVP08 creates the contract that a later controlled-delivery implementation must satisfy. MVP08 does not perform outbound delivery and does not unlock the protected delivery path.

## Source evidence

```text
source_work_package=ETF-EU-MVP07
sender_entrypoint_validated=true
controlled_send_preflight_status=ready_for_future_delivery
sender_preflight_artifact=output/delivery/etf_eu_sender_preflight_20260708_000000.json
controlled_send_preflight_manifest=output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json
base_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
```

## Rolemodel alignment

The weekly-etf rolemodel writes a redaction-safe delivery manifest summary after the transport layer returns without exception, then references that manifest from the final run manifest and validates evidence.

ETF EU must port that behavior without importing U.S. report-name assumptions.

## Delivery evidence rule

Future ETF EU delivery evidence must be a delivery manifest summary, not an inbox receipt claim.

## Delivery status rule

Future delivery status values are:

```text
not_attempted
smtp_sendmail_returned_no_exception
smtp_sendmail_failed
evidence_invalid
```

## Delivery status caveat rule

Future transport success evidence must state:

```text
sendmail returned without raising and wrote per-language delivery manifest evidence; this is not an end-recipient inbox receipt
```

## Recipient redaction rule

Future delivery evidence must use:

```text
recipient_data_policy=redacted_hash_only
recipient_hash_required=true
recipient_redacted_required=true
recipient_plaintext_values_exposed=false
secret_values_exposed=false
```

## Language evidence rule

Future delivery evidence must include both:

```text
nl = Dutch primary client report
en = English companion report
```

Each language evidence object must include report path, source manifest path, source manifest type, timestamp, mode, report, recipient hash, redaction flag, body evidence flag, attachment evidence, attachment count and PDF attachment list.

## PDF evidence rule

If PDFs are generated for controlled delivery, future evidence must prove PDF attachment presence per language.

## Final run-bundle evidence rule

Future ETF EU controlled delivery evidence must be referenced by the final EU run bundle.

## Workflow guard rule

MVP08 does not remove the existing workflow guard. A later implementation must use a tested replacement guard before any protected delivery path is used.

## Failure handling rule

Future implementation must fail closed when delivery evidence is missing, the caveat is missing, redaction fails, the language pair is incomplete, run-bundle reference is missing, private runtime values are exposed, or recipient plaintext is exposed.

## Success claim rule

Future delivery success claim requires validated delivery evidence. MVP08 does not claim success.

## Privacy and secret handling rule

MVP08 must not expose private runtime values or recipient values.

## What this package may create

```text
controlled-send delivery evidence contract
MVP08 artifact
MVP08 notes
MVP08 validator
MVP08 tests
MVP08 decision record
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
delivery_success_claimed=false
```

## Next package

```text
ETF-EU-MVP09 — ETF EU controlled-send implementation with delivery evidence
```

## Validation requirements

The MVP08 validator must confirm the contract, artifact and notes exist; delivery evidence status is contract_defined_not_executed; redacted recipient policy is required; NL and EN language evidence are required; final run-bundle reference and evidence validator are required; all delivery execution flags remain false; the workflow guard remains present; and selected_next_package=ETF-EU-MVP09.
