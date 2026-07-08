# ETF-EU-MVP06 sender entrypoint implementation or validation

## Scope

MVP06 implemented and validated an EU-specific sender preflight entrypoint.

MVP06 does not send the report.

MVP06 keeps the workflow send guard present.

## Source evidence

```text
source_work_package=ETF-EU-MVP05
latest_validated_workflow_mode=dry_run
validate_only_status=green
dry_run_status=green
latest_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
latest_run_bundle=output/runs/20260708_142840/etf_eu_run_bundle_manifest.json
delivery_manifest_validation=passed
run_bundle_validation=passed
```

## Sender entrypoint implemented

```text
eu_sender_entrypoint_created=true
eu_sender_entrypoint_selected=true
eu_sender_entrypoint_selected_path=runtime/send_etf_eu_report_runtime_html.py
sender_entrypoint_validated=true
sender_entrypoint_validation_status=validated_no_send
```

## Sender preflight behavior

```text
preflight_no_send_mode_supported=true
send_performed=false
production_delivery=false
email_delivery=false
delivery_receipt=false
delivery_success_claimed=false
```

## Dutch-primary and English companion support

```text
dutch_primary_supported=true
english_companion_supported=true
```

The entrypoint selects canonical EU Dutch primary and English companion reports.

## Non-canonical artifact handling

```text
non_canonical_artifacts_ignored=true
us_report_name_assumption_detected=false
```

The entrypoint ignores non-canonical draft artifacts and does not select inherited U.S. report names.

## Send guard decision

```text
workflow_send_guard_present=true
workflow_send_guard_removed=false
delivery_mode_send_unlocked=false
send_enablement_allowed=false
send_enablement_status=blocked_pending_manifest_transition_and_receipt_rules
```

## Boundaries preserved

```text
production_delivery=false
email_delivery=false
delivery_receipt=false
delivery_success_claimed=false
delivery_success_claim_allowed=false
secret_values_exposed=false
recipient_plaintext_values_exposed=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
pricing_evidence_changed=false
source_pdf_replaced=false
new_pdf_created=false
renderer_changed=false
```

## Decision

```text
MVP06 implemented or validated the EU sender preflight entrypoint.
The entrypoint selects canonical EU Dutch primary and English companion reports.
The entrypoint ignores non-canonical draft artifacts.
The entrypoint does not use U.S. weekly_analysis report names.
The entrypoint does not send the report.
The workflow send guard remains present.
```

## Next package

```text
ETF-EU-MVP07 — ETF EU manifest transition and controlled-send preflight
```
