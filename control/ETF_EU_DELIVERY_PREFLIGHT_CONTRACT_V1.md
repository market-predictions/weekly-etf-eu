# ETF EU delivery-preflight contract v1

## Purpose

Define delivery-preflight requirements for the ETF EU report workflow after client-grade report-state authority has been created.

## Scope

This contract defines delivery-preflight requirements only. It applies to the committed ETF EU evidence chain through ETF-EU-WP15AL.

## Authority boundary

```text
delivery_preflight_allowed=false
production_delivery=false
receipt_artifact_created=false
production_manifest_created=false
recipient_config_changed=false
smtp_or_secret_config_changed=false
recipient_authority_created=false
transport_authority_created=false
```

## Delivery-preflight state model

```text
client_grade_status=authorized_no_delivery
delivery_preflight_allowed=false
delivery_authorization_decision=remain_blocked
production_delivery=false
```

Delivery-preflight can only be opened by a later explicit authority package.

## Production manifest contract

A future production manifest must include:

```text
run_id
commit_sha
workflow_run_id
source_report_path
source_pdf_hash
recipient_set_reference
transport_reference
send_timestamp
delivery_status
receipt_artifact_path
post_send_verification_status
rollback_status
```

The manifest contract is defined here, but no production manifest is created by this package.

## Delivery receipt contract

A future delivery receipt must include:

```text
send_attempt_id
transport
recipient_set_reference
message_id_or_transport_receipt
send_timestamp
send_result
verification_timestamp
verification_result
failure_reason
```

The receipt contract is defined here, but no delivery receipt is created by this package.

## Recipient authority gate

```text
gate_status=defined_not_authorized
recipient_config_changed=false
recipient_authority_created=false
required_future_authority=recipient_configuration_authority
blocking_status=blocking_delivery_preflight
```

## Transport authority gate

```text
gate_status=defined_not_authorized
smtp_or_secret_config_changed=false
transport_authority_created=false
required_future_authority=SMTP_secret_authority
blocking_status=blocking_delivery_preflight
```

## Preflight evidence requirements

Delivery-preflight requires:

```text
client_grade_authority_decision
client_grade_pdf_or_report_artifact
production_manifest_contract
delivery_receipt_contract
recipient_authority
transport_authority
outbound_runbook
post_send_verification_loop
rollback_abort_policy
explicit_delivery_preflight_authority
```

## What this contract does not authorize

```text
send_report=false
create_delivery_receipt=false
create_production_manifest=false
change_recipients=false
change_transport_config=false
create_transport_authority=false
create_recipient_authority=false
production_delivery=false
```

## Validation requirements

A validator must confirm this contract exists, required sections are present, all no-authority flags remain false, recipient and transport authority remain false, and the selected next package is ETF-EU-WP15AN or ETF-EU-WP15AM-FIX.
