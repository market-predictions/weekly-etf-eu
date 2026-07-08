# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP07 — ETF EU manifest transition and controlled-send preflight**.

## Latest completion

```text
work_package_id=ETF-EU-MVP06
status=completed_sender_entrypoint_validated_no_send
source_work_package=ETF-EU-MVP05
eu_sender_entrypoint_created=true
eu_sender_entrypoint_selected=true
eu_sender_entrypoint_selected_path=runtime/send_etf_eu_report_runtime_html.py
sender_entrypoint_validated=true
sender_entrypoint_validation_status=validated_no_send
preflight_no_send_mode_supported=true
dutch_primary_supported=true
english_companion_supported=true
us_report_name_assumption_detected=false
non_canonical_artifacts_ignored=true
latest_validated_workflow_mode=dry_run
validate_only_status=green
dry_run_status=green
latest_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
latest_run_bundle=output/runs/20260708_142840/etf_eu_run_bundle_manifest.json
delivery_manifest_validation=passed
run_bundle_validation=passed
delivery_enabled=false
production_delivery=false
email_delivery=false
delivery_receipt=false
send_performed=false
send_enablement_allowed=false
delivery_mode_send_unlocked=false
workflow_send_guard_present=true
workflow_send_guard_removed=false
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
selected_next_package=ETF-EU-MVP07
```

## Active next package

```text
ETF-EU-MVP07 — ETF EU manifest transition and controlled-send preflight
```

Purpose:

```text
Validate delivery manifest transition and controlled-send preflight rules using the EU sender preflight entrypoint, while keeping delivery_mode=send locked until receipt and success-claim evidence rules are complete.
```

## Scope guardrails

```text
Do not run delivery_mode=send.
Do not remove the workflow send guard.
Do not claim delivery success without real receipt evidence.
Do not mutate portfolio state.
Do not create valuation-grade authority.
Do not create funding authority.
Do not create funded positions.
Do not change recommendation logic in production.
Do not expose private runtime values.
Do not expose recipient values.
Do not return to manual evidence templates.
Do not return to WP15 abstract gates unless a concrete validator failure occurs.
```
