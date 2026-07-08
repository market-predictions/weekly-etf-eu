# ETF-EU-MVP08 controlled-send delivery evidence contract

## Scope

MVP08 defines the controlled-send delivery evidence contract.

MVP08 does not perform outbound delivery, does not unlock the protected delivery path, does not remove the workflow guard, does not create inbox receipt evidence, and does not claim delivery success.

## Source evidence

```text
source_work_package=ETF-EU-MVP07
source_mvp07_artifact=output/client_surface/etf_eu_mvp07_manifest_transition_and_controlled_send_preflight_20260708_000000.json
sender_preflight_artifact=output/delivery/etf_eu_sender_preflight_20260708_000000.json
controlled_send_preflight_manifest=output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json
base_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
latest_run_bundle=output/runs/20260708_142840/etf_eu_run_bundle_manifest.json
```

## Rolemodel alignment

MVP08 aligns ETF EU with the weekly-etf delivery manifest summary pattern: transport evidence, redacted recipient policy, language evidence, final run manifest reference, and evidence validation.

## Delivery evidence contract

```text
controlled_send_delivery_evidence_contract_created=true
controlled_send_delivery_evidence_contract_validated=true
delivery_evidence_status=contract_defined_not_executed
future_delivery_status_values_defined=true
evidence_validator_required=true
final_run_bundle_reference_required=true
```

## Delivery status caveat

Future transport evidence may record `smtp_sendmail_returned_no_exception` only after real execution and must state that this is not an end-recipient inbox receipt.

## Recipient redaction

```text
recipient_data_policy=redacted_hash_only
recipient_hash_required=true
recipient_redacted_required=true
recipient_plaintext_values_exposed=false
secret_values_exposed=false
```

## Language evidence

```text
required_languages=nl,en
dutch_primary_language=nl
english_companion_language=en
language_count_required=2
```

## Final run-bundle evidence

Future controlled delivery evidence must be referenced by the final EU run bundle before any success claim is allowed.

## Failure handling

```text
fail_closed_without_delivery_evidence=true
fail_closed_without_status_caveat=true
fail_closed_without_recipient_redaction=true
fail_closed_without_language_pair=true
fail_closed_without_run_bundle_reference=true
fail_closed_on_secret_exposure=true
fail_closed_on_recipient_exposure=true
```

## Send guard decision

```text
workflow_send_guard_present=true
workflow_send_guard_removed=false
delivery_mode_send_unlocked=false
send_enablement_allowed=false
send_enablement_status=blocked_pending_mvp09_implementation
```

## Boundaries preserved

```text
receipt_file_created=false
delivery_enabled=false
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
send_performed=false
delivery_success_claimed=false
delivery_success_claim_allowed=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

## Decision

```text
MVP08 defined and validated the controlled-send delivery evidence contract.
MVP08 aligned ETF EU with the weekly-etf delivery manifest summary pattern.
MVP08 did not perform outbound delivery.
MVP08 did not unlock delivery_mode=send.
MVP08 did not remove the workflow guard.
MVP08 did not create inbox receipt evidence.
MVP08 did not claim delivery success.
```

## Next package

```text
ETF-EU-MVP09 — ETF EU controlled-send implementation with delivery evidence
```
