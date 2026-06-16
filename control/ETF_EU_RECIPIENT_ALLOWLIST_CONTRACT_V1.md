# ETF EU Recipient Allowlist Contract V1

## Purpose

This contract defines the inactive/sample-only recipient allowlist format for the Weekly ETF EU report system.

It is an **input/state contract and validation contract only**. It does not enable recipient activation, SMTP, mail transport, email sending, PDF generation, delivery receipts, production delivery, funding authority, portfolio mutation, candidate promotion or valuation-grade authority.

## Current recipient allowlist status

The current implementation must remain sample-only and inactive:

```text
schema_version=etf_eu_recipient_allowlist_v1
status=sample_only_inactive
recipient_activation=false
real_recipients=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
```

## Four-layer separation

### 1. Decision framework

The allowlist contract may define the shape of a future recipient allowlist.

It is not a portfolio decision, fundability decision, pricing decision, candidate-promotion decision, send authorization or delivery proof.

### 2. Input/state contract

The sample allowlist may contain only non-real placeholder recipients.

Allowed placeholder recipient email domain:

```text
@example.invalid
```

No real user, client, company, broker, Gmail, Outlook or private-domain email addresses may be added in this phase.

### 3. Output contract

The sample allowlist lives at:

```text
config/etf_eu_recipient_allowlist.sample.yml
```

This file is not a production allowlist and must not be used for production delivery.

Required top-level fields:

```text
schema_version
status
recipient_activation
real_recipients
send_attempted
email_delivery
production_delivery
delivery_receipt
recipients
```

Required recipient fields:

```text
recipient_id
display_name
email
role
active
delivery_enabled
notes
```

### 4. Operational runbook

This package may add:

```text
control/ETF_EU_RECIPIENT_ALLOWLIST_CONTRACT_V1.md
config/etf_eu_recipient_allowlist.sample.yml
tools/validate_etf_eu_recipient_allowlist.py
tests/test_etf_eu_recipient_allowlist.py
```

It must not be wired to:

```text
mail transport
external mail API send
SMTP configuration
recipient activation
PDF generation
delivery receipt creation
production delivery
portfolio mutation
candidate promotion
```

## Sample-only recipient rules

The sample allowlist must keep:

```text
status=sample_only_inactive
recipient_activation=false
real_recipients=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
```

Each recipient must keep:

```text
active=false
delivery_enabled=false
```

Each recipient email must end with:

```text
@example.invalid
```

## Forbidden live-delivery keys

The sample allowlist and nested recipient objects must not contain live delivery or SMTP-related keys, including:

```text
smtp_host
smtp_user
smtp_password
api_key
mail_transport
sendgrid
mailgun
gmail
outlook
```

## Future authority rule

Real recipient activation requires a later explicit authority decision and validator-backed production allowlist contract.

WP12C does not create that authority.

## Current rule

WP12C may create this contract, sample allowlist, validator, tests and sample validation evidence.

WP12C must not:

```text
start WP13
add mail transport configuration
add real recipients
add SMTP secrets
send email
generate production PDFs
create a real delivery receipt
claim production delivery
mutate portfolio state
promote candidates
alter pricing authority
treat Twelve Data as valuation authority
wire this sample allowlist into a live workflow
activate recipients
```
