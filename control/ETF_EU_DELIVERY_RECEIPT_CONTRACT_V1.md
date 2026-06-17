# ETF EU Delivery Receipt Contract V1

## Purpose

This contract defines the sample-only delivery receipt validator shape for the Weekly ETF EU report system.

It is an input/state contract and output validation contract only. It does not enable real delivery, email sending, recipient activation, mail transport, PDF generation, production delivery, funding authority, portfolio mutation, candidate promotion or valuation-grade authority.

## Current receipt status

The current implementation must remain sample-only and not delivery proof:

```text
schema_version=etf_eu_delivery_receipt_v1
status=sample_only_not_delivery
receipt_type=sample_only
delivery_attempted=false
delivery_success=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
pdf_generation=false
recipient_activation=false
mail_transport_enabled=false
```

## Four-layer separation

### 1. Decision framework

The receipt validator may define what a future receipt must prove.

It is not a portfolio decision, fundability decision, pricing decision, candidate-promotion decision, send authorization or delivery proof.

### 2. Input/state contract

The sample receipt may contain only non-delivery placeholder evidence.

A sample receipt must not contain:

```text
real recipient references
provider confirmations
transport message IDs
real delivery artifact paths
live delivery channel
```

### 3. Output contract

The sample receipt lives at:

```text
output/delivery/etf_eu_delivery_receipt_sample_20260617_000000.json
```

This file is not production delivery proof and must not be used as a real delivery receipt.

Required top-level fields:

```text
schema_version
run_id
created_at_utc
report_date
status
receipt_type
delivery_attempted
delivery_success
send_attempted
email_delivery
production_delivery
delivery_receipt
pdf_generation
recipient_activation
mail_transport_enabled
channel
recipient_reference
delivery_artifact_paths
provider_confirmation
transport_message_id
blockers
```

### 4. Operational runbook

This package may add:

```text
control/ETF_EU_DELIVERY_RECEIPT_CONTRACT_V1.md
output/delivery/etf_eu_delivery_receipt_sample_20260617_000000.json
tools/validate_etf_eu_delivery_receipt.py
tests/test_etf_eu_delivery_receipt.py
```

It must not be wired to:

```text
mail transport
external mail API send
recipient activation
PDF generation
real delivery receipt creation
production delivery
portfolio mutation
candidate promotion
```

## Sample-only receipt rules

The sample receipt must keep:

```text
status=sample_only_not_delivery
receipt_type=sample_only
delivery_attempted=false
delivery_success=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
pdf_generation=false
recipient_activation=false
mail_transport_enabled=false
channel=none
recipient_reference=null
delivery_artifact_paths=[]
provider_confirmation=null
transport_message_id=null
```

The sample receipt blockers must include:

```text
sample receipt only
no delivery attempted
no provider confirmation
no recipient activation
real delivery not authorized
```

## Future authority rule

A future real receipt must be separate from the manifest and must include a concrete delivery channel, timestamp, recipient reference, artifact references and provider/transport confirmation.

A future real receipt requires explicit delivery authority and validator-backed operational proof.

WP12E does not create that authority.

## Current rule

WP12E may create this contract, sample-only receipt, validator and tests.

WP12E must not:

```text
start WP13
implement real delivery
send email
add real recipients
add secrets
activate mail transport
generate production PDFs
create a real delivery receipt
create provider confirmation
create transport message IDs
mutate portfolio state
promote candidates
alter pricing authority
treat Twelve Data as valuation authority
wire this sample receipt validator into a live workflow
```
