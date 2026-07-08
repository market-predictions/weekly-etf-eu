# ETF EU MVP07 manifest transition and controlled-send preflight v1

## Purpose

MVP07 creates and validates a controlled-send preflight manifest for ETF EU.

## Scope

MVP07 proves that ETF EU can transition from a blocked design-only manifest to a safe preflight-ready manifest state without performing delivery.

## Source evidence

```text
source_work_package=ETF-EU-MVP06
sender_entrypoint_validated=true
sender_entrypoint_validation_status=validated_no_send
latest_validated_workflow_mode=dry_run
validate_only_status=green
dry_run_status=green
base_delivery_manifest=output/delivery/etf_eu_delivery_manifest_20260708_142840.json
latest_run_bundle=output/runs/20260708_142840/etf_eu_run_bundle_manifest.json
```

## Manifest transition rule

MVP07 may create a preflight manifest with:

```text
status=ready_for_future_delivery
delivery_enabled=false
receipt_status=pending
```

This is not a sent state and not proof of actual delivery.

## Controlled-send preflight rule

The controlled-send preflight manifest must preserve all delivery authority flags as false.

## Sender preflight evidence rule

MVP07 must include sender preflight evidence showing:

```text
preflight_no_send_mode_supported=true
send_performed=false
production_delivery=false
email_delivery=false
delivery_receipt=false
delivery_success_claimed=false
```

## Receipt reservation rule

MVP07 may reserve a future receipt path but must not create a receipt file.

## Send guard rule

The workflow send guard must remain present.

## Success claim rule

MVP07 must not claim delivery success.

## What this package may create

```text
sender preflight evidence
controlled-send preflight manifest
controlled-send preflight manifest validator
MVP07 artifact, notes, tests and decision record
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
ETF-EU-MVP08 — ETF EU controlled-send unlock or receipt contract
```

## Validation requirements

The MVP07 validator must confirm that the controlled-send preflight manifest is ready_for_future_delivery, delivery_enabled remains false, the future receipt path is reserved but no receipt file exists, no delivery authority is created, the workflow send guard remains present, no success claim is made, and selected_next_package=ETF-EU-MVP08.
