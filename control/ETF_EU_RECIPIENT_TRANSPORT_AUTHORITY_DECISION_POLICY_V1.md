# ETF EU recipient and transport authority decision policy v1

## Purpose

Create an explicit recipient and transport authority decision after the WP15AO evidence-contract package.

## Scope

This policy creates only an authority decision. It does not execute recipient, transport, delivery, portfolio, pricing, or PDF changes.

## Authority boundary

```text
recipient_authority_created=false
transport_authority_created=false
recipient_config_changed=false
smtp_or_secret_config_changed=false
secret_values_exposed=false
recipient_plaintext_values_exposed=false
delivery_preflight_allowed=false
production_delivery=false
receipt_artifact_created=false
production_manifest_created=false
```

## Required recipient evidence

A positive recipient authority decision requires committed evidence before this package starts:

```text
recipient_set_reference_id
recipient_set_hash
recipient_owner_approval_reference
recipient_rollback_reference
recipient_plaintext_values_exposed=false
recipient_config_changed=false
```

## Required transport evidence

A positive transport authority decision requires committed evidence before this package starts:

```text
transport_reference_id
transport_presence_check_reference
transport_owner_approval_reference
transport_rollback_reference
secret_values_exposed=false
smtp_or_secret_config_changed=false
```

## Secret-handling decision rule

```text
secret_values_exposed=false
secret_reference_names_only=true
transport_config_changed=false
```

## Recipient-handling decision rule

```text
recipient_plaintext_values_exposed=false
recipient_reference_or_hash_only=true
recipient_config_changed=false
```

## Positive authority decision rule

Positive authority requires concrete committed recipient and transport evidence before this package starts.

## Negative authority decision rule

Negative authority keeps recipient_authority_created=false and transport_authority_created=false.

## What this policy does not authorize

```text
change_recipient_configuration=false
change_transport_configuration=false
expose_secret_values=false
expose_plaintext_recipient_values=false
send_report=false
create_delivery_receipt=false
create_production_manifest=false
open_delivery_preflight=false
create_production_delivery=false
```

## Validation requirements

A validator must confirm this policy exists, the expected negative decision branch is internally consistent, all no-authority and no-delivery flags remain false, source price/PDF rows remain unchanged, and selected_next_package is ETF-EU-WP15AQ or ETF-EU-WP15AP-FIX.
