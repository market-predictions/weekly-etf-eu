# ETF EU recipient and transport authority evidence contract v1

## Purpose

Define the evidence requirements needed before a later package can create recipient configuration authority or transport configuration authority for ETF EU delivery workflows.

## Scope

This contract defines recipient and transport authority evidence requirements only.

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

## Recipient authority evidence contract

Future recipient authority evidence must use references and hashes, not plaintext recipient values.

Required future evidence fields:

```text
recipient_authority_evidence_status
recipient_set_reference_id
recipient_set_hash_required
recipient_plaintext_values_allowed=false
recipient_owner_approval_reference_required
recipient_change_scope
recipient_change_authority_required
recipient_validation_method
recipient_rollback_reference_required
recipient_authority_created=false
recipient_config_changed=false
```

## Transport authority evidence contract

Future transport authority evidence must use reference names and presence checks, not secret values.

Required future evidence fields:

```text
transport_authority_evidence_status
transport_reference_id
transport_secret_reference_names_allowed=true
transport_secret_values_allowed=false
transport_presence_check_required
transport_owner_approval_reference_required
transport_change_scope
transport_change_authority_required
transport_validation_method
transport_rollback_reference_required
transport_authority_created=false
smtp_or_secret_config_changed=false
```

## Secret-handling boundary

This contract does not expose secret values. Future evidence may use reference names and presence checks only.

## Recipient-handling boundary

This contract does not expose plaintext recipient values. Future evidence may use recipient set references and hashes only.

## Evidence sufficiency rules

Recipient evidence is sufficient for contract definition only when reference id, hash requirement, owner approval reference requirement, validation method, and rollback reference requirement are defined.

Transport evidence is sufficient for contract definition only when transport reference id, reference-name-only handling, presence check requirement, owner approval reference requirement, validation method, and rollback reference requirement are defined.

## Positive evidence contract rule

A positive evidence-contract result means only that future evidence requirements are defined and validated. It does not create authority.

## Negative authority rule

Recipient authority and transport authority remain false until a later explicit authority package creates them from committed evidence.

## What this contract does not authorize

```text
create_recipient_authority=false
create_transport_authority=false
change_recipient_configuration=false
change_transport_configuration=false
expose_secret_values=false
expose_plaintext_recipient_values=false
send_report=false
create_delivery_receipt=false
create_production_manifest=false
open_delivery_preflight=false
```

A later explicit authority package is required before recipient or transport authority may be created.

A later explicit delivery-preflight authority package is required before preflight execution may open.

## Validation requirements

A validator must confirm this contract exists, required sections are present, evidence contracts are defined, no authority is created, no recipient or transport configuration is changed, no sensitive values are exposed, no delivery artifact is created, source price/PDF rows remain unchanged, and selected_next_package is ETF-EU-WP15AP or ETF-EU-WP15AO-FIX.
