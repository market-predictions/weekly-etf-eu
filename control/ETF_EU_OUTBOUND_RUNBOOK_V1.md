# ETF EU outbound runbook v1

## Purpose

Define the contract-only outbound runbook for the ETF EU report workflow.

## Scope

This runbook is a contract-only runbook. It describes gates and abort conditions but does not execute delivery.

## Preconditions

```text
client_grade_status=authorized_no_delivery
delivery_preflight_allowed=false
recipient_authority_created=false
transport_authority_created=false
production_delivery=false
```

## Preflight checklist

Required checks before any later delivery-preflight authority package may open execution:

```text
client_grade_authority_decision
source_report_or_pdf_artifact
production_manifest_contract
delivery_receipt_contract
recipient_authority_gate
transport_authority_gate
post_send_verification_loop
rollback_abort_policy
explicit_delivery_preflight_authority
```

## Recipient gate

The recipient gate is defined but not authorized.

```text
recipient_config_changed=false
recipient_authority_created=false
blocking_status=blocking_delivery_preflight
```

## Transport gate

The transport gate is defined but not authorized.

```text
smtp_or_secret_config_changed=false
transport_authority_created=false
blocking_status=blocking_delivery_preflight
```

## Manifest gate

The manifest gate requires a later production manifest artifact. This runbook does not create it.

## Delivery execution gate

Delivery execution is blocked.

```text
delivery_preflight_allowed=false
delivery_execution_allowed=false
production_delivery=false
```

## Post-send verification handoff

Post-send verification requirements are defined in the verification and rollback policy. No verification is executable until a later package authorizes delivery and creates real delivery evidence.

## Abort conditions

Abort before send if any required gate is missing, any source artifact is missing, any authority is absent, or any no-authority flag is unexpectedly true.

## What this runbook does not authorize

```text
send_report=false
authorize_delivery=false
create_delivery_artifacts=false
modify_transport_or_recipients=false
```

A later explicit authority package is required before any delivery-preflight or sending.

## Validation requirements

A validator must confirm that the runbook exists, required sections are present, execution remains false, and no delivery artifact has been created.
