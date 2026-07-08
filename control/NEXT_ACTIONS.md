# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP06 — ETF EU sender entrypoint implementation or validation**.

## Latest completion

```text
work_package_id=ETF-EU-MVP05
status=completed_sender_entrypoint_validation_scaffold
source_work_package=ETF-EU-MVP04-FIX-VALIDATE-ONLY-02
latest_validated_workflow_mode=dry_run
validate_only_status=green
dry_run_status=green
latest_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
latest_run_bundle=output/runs/20260708_142840/etf_eu_run_bundle_manifest.json
delivery_manifest_validation=passed
run_bundle_validation=passed
delivery_manifest_status=available
delivery_enabled=false
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
sender_entrypoint_validation_created=true
sender_entrypoint_inventory_created=true
sender_entrypoint_validated=false
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
selected_next_package=ETF-EU-MVP06
```

## Active next package

```text
ETF-EU-MVP06 — ETF EU sender entrypoint implementation or validation
```

Purpose:

```text
Implement or validate an EU-specific sender entrypoint that preserves Dutch-primary and English companion semantics, supports a preflight/no-send mode, integrates with delivery and run manifests, and keeps delivery_mode=send locked until controlled-send evidence is complete.
```

## Scope guardrails

```text
Do not run delivery_mode=send.
Do not remove the workflow send guard until sender entrypoint validation, manifest transition logic, receipt evidence rules, and tests are complete.
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
