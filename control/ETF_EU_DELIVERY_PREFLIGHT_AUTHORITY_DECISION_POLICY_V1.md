# ETF EU delivery-preflight authority decision policy v1

## Purpose

Define the explicit delivery-preflight authority decision after the WP15AM contract/runbook package.

## Scope

This policy creates only a delivery-preflight authority decision. It does not execute delivery-preflight.

## Authority boundary

```text
delivery_ready=false
production_delivery=false
receipt_artifact_created=false
production_manifest_created=false
recipient_config_changed=false
smtp_or_secret_config_changed=false
recipient_authority_created=false
transport_authority_created=false
```

## Required authority inputs

```text
client_grade_authority_decision
delivery_preflight_contract
production_manifest_contract
delivery_receipt_contract
outbound_runbook
post_send_verification_loop
rollback_abort_policy
recipient_authority_gate
transport_authority_gate
explicit_delivery_preflight_authority
```

## Recipient authority sufficiency rule

A positive decision requires committed recipient authority evidence before this package starts. WP15AN does not create recipient authority.

## Transport authority sufficiency rule

A positive decision requires committed transport authority evidence before this package starts. WP15AN does not create transport authority.

## Explicit delivery-preflight authority rule

A positive decision requires explicit delivery-preflight authority evidence before execution can open. Without it, delivery-preflight remains blocked.

## Positive authority decision rule

A positive decision is allowed only if recipient authority, transport authority, and explicit delivery-preflight authority already exist as committed evidence.

## Negative authority decision rule

A negative decision must keep delivery-preflight blocked and must keep all delivery artifact flags false.

## What this policy does not authorize

```text
send_report=false
create_production_delivery=false
create_delivery_receipt=false
create_production_manifest=false
change_recipients=false
change_transport_config=false
create_recipient_authority=false
create_transport_authority=false
```

## Validation requirements

A validator must confirm the policy exists, the decision branch is internally consistent, no delivery artifacts are created, no recipient or transport authority is created, source price/PDF rows remain unchanged, and selected_next_package is ETF-EU-WP15AO or ETF-EU-WP15AN-FIX.
