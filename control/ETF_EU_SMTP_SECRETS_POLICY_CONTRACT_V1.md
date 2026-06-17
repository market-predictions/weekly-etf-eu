# ETF EU SMTP Secrets Policy Contract V1

## Purpose

This contract defines the documentation-only SMTP/secrets policy format for the Weekly ETF EU report system.

It is an input/state contract and validation contract only. It does not enable mail transport, SMTP configuration, external mail APIs, email sending, delivery receipts, production delivery, funding authority, portfolio mutation, candidate promotion or valuation-grade authority.

## Current SMTP/secrets policy status

The current implementation must remain sample-only and no-secrets:

```text
schema_version=etf_eu_smtp_secrets_policy_v1
status=sample_only_no_secrets
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
```

## Four-layer separation

### 1. Decision framework

The SMTP/secrets policy contract may define the shape of a future secure mail-transport policy.

It is not a portfolio decision, fundability decision, pricing decision, candidate-promotion decision, send authorization or delivery proof.

### 2. Input/state contract

The sample policy may contain only non-secret placeholder values.

Allowed placeholder values:

```text
placeholder.invalid
placeholder_only
FUTURE_PLACEHOLDER
0
false
```

No real mail host, account name, token, credential, provider endpoint, provider account, client account, broker account, private-domain value or secret value may be stored in the repository.

### 3. Output contract

The sample policy lives at:

```text
config/etf_eu_smtp_secrets_policy.sample.yml
```

This file is not a production SMTP configuration and must not be used for production delivery.

Required top-level fields:

```text
schema_version
status
smtp_configured
secrets_present
mail_transport_enabled
external_mail_api_enabled
send_attempted
email_delivery
production_delivery
delivery_receipt
secret_storage_policy
transport_policy
notes
```

Required `secret_storage_policy` fields:

```text
storage_location
repo_plaintext_secrets_allowed
secret_values_in_repo_allowed
required_future_secret_names
```

Required `transport_policy` fields:

```text
smtp_host
smtp_port
smtp_username
smtp_secret_reference
provider
active
delivery_enabled
```

### 4. Operational runbook

This package may add:

```text
control/ETF_EU_SMTP_SECRETS_POLICY_CONTRACT_V1.md
config/etf_eu_smtp_secrets_policy.sample.yml
tools/validate_etf_eu_smtp_secrets_policy.py
tests/test_etf_eu_smtp_secrets_policy.py
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

## Sample-only rules

The sample policy must keep:

```text
status=sample_only_no_secrets
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
```

The transport policy must keep:

```text
smtp_host=placeholder.invalid
smtp_port=0
smtp_username=placeholder_only
smtp_secret_reference=placeholder_only
provider=placeholder_only
active=false
delivery_enabled=false
```

The storage policy must keep:

```text
repo_plaintext_secrets_allowed=false
secret_values_in_repo_allowed=false
```

## Future authority rule

Real SMTP/secrets activation requires a later explicit authority decision, secure secret storage outside the repository, and validator-backed delivery receipt handling.

WP12D does not create that authority.

## Current rule

WP12D may create this contract, sample no-secrets policy, validator, tests and sample validation evidence.

WP12D must not:

```text
start WP13
add mail transport configuration
add real recipients
add secrets
send email
generate production PDFs
create a real delivery receipt
claim production delivery
mutate portfolio state
promote candidates
alter pricing authority
treat Twelve Data as valuation authority
wire this sample policy into a live workflow
activate mail transport
```
