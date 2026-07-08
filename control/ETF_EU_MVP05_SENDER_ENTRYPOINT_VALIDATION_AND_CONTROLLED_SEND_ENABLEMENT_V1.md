# ETF EU MVP05 sender entrypoint validation and controlled send enablement v1

## Purpose

Validate the ETF EU sender entrypoint and controlled-send requirements against the weekly-etf rolemodel.

## Scope

MVP05 creates sender-entrypoint validation and controlled-send enablement rules. MVP05 does not send the report and does not unlock delivery_mode=send.

## Rolemodel authority

The weekly-etf rolemodel performs a separate send step through GitHub Actions environment values and then writes delivery/run manifest evidence. ETF EU must port that behavior without importing U.S. report-name assumptions.

## Confirmed dry-run evidence

```text
validate_only_status=green
dry_run_status=green
latest_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
latest_run_bundle=output/runs/20260708_142840/etf_eu_run_bundle_manifest.json
delivery_manifest_validation=passed
run_bundle_validation=passed
delivery_manifest_status=available
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
```

## Sender entrypoint inventory

Candidate entrypoints:

```text
send_report_runtime_html.py
send_report.py
```

The inventory is created, but no EU sender entrypoint is selected by this package.

## Sender entrypoint validation rule

A sender entrypoint is valid only after it supports EU Dutch-primary and English companion report selection, preflight/no-send behavior, rolemodel environment names, delivery manifest transition evidence, and run bundle evidence.

## Dutch-primary delivery rule

ETF EU delivery must treat the Dutch report as the primary client report.

## English companion delivery rule

ETF EU delivery may include the English report as a companion/operator-facing artifact.

## Secret-name rule

MVP05 validates rolemodel secret-name usage through workflow environment only. It must not expose values.

## No-private-value exposure rule

MVP05 must not expose private runtime values or recipient values.

## Send guard rule

The workflow send guard remains present until a later package validates sender entrypoint behavior and controlled-send manifest transitions.

## Delivery manifest transition rule

A future send-enabled path must transition the delivery manifest from design/dry-run status to a controlled pre-send or sent status only when evidence exists.

## Run bundle transition rule

A future send-enabled path must include sender-entrypoint validation and delivery evidence in the run bundle.

## Receipt rule

Delivery success requires a real receipt artifact.

## Success claim rule

MVP05 cannot claim delivery success.

## What this package may validate

```text
sender_entrypoint_inventory=true
sender_entrypoint_validation_rules=true
send_guard_rule=true
manifest_transition_rule=true
run_bundle_transition_rule=true
receipt_rule=true
success_claim_rule=true
```

## What this package must not execute

```text
production_delivery=false
email_delivery=false
delivery_receipt=false
delivery_success_claimed=false
workflow_send_guard_removed=false
delivery_mode_send_unlocked=false
```

## Next package

```text
ETF-EU-MVP06 — ETF EU sender entrypoint implementation or validation
```

## Validation requirements

The MVP05 validator must confirm dry-run evidence, sender validation scaffold fields, send guard preservation, no delivery, no success claim, required nested objects, and selected_next_package=ETF-EU-MVP06.
