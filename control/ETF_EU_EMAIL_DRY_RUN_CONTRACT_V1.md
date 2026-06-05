# ETF EU Email Dry-Run Contract V1

## Purpose

This contract defines the email delivery dry-run artifact for the Weekly ETF EU report system.

It is a **design-only email delivery preparation contract**. It does not enable mail transport, external mail APIs, recipient activation, PDF generation, delivery receipts, or production delivery.

## Current email delivery status

```text
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

## Four-layer separation

### 1. Decision framework

The email dry-run package may describe how an already validated Dutch-first EU report would be packaged for a future delivery review.

It is not a portfolio decision, pricing decision, fundability decision, candidate-promotion mechanism, delivery authorization, or client-delivery proof.

### 2. Input/state contract

An email dry-run artifact may reference only already produced or explicitly placeholder artifacts:

```text
output/weekly_etf_eu_review_nl_*.md
output/weekly_etf_eu_review_*.md
output/delivery/etf_eu_delivery_manifest_*.json
output/pdf/*.pdf
```

If the delivery manifest path is not available, the dry-run artifact must use:

```text
delivery_manifest_path=null
delivery_manifest_status=not_available
```

If shadow PDF paths are not available, the dry-run artifact must use:

```text
pdf_paths_or_null=null
pdf_status=not_available
```

The dry-run artifact must not create or change portfolio state.

### 3. Output contract

The email dry-run artifact is a machine-readable control artifact under:

```text
output/delivery/email_dry_run_<run_id>.json
```

Required top-level fields:

```text
schema_version
run_id
created_at_utc
report_date
status
recipient_allowlist_status
subject_preview
body_preview
attachment_paths
delivery_manifest_path
delivery_manifest_status
pdf_paths_or_null
pdf_status
send_attempted
email_delivery
delivery_receipt
production_delivery
authority
blockers
```

Allowed `schema_version`:

```text
etf_eu_email_dry_run_v1
```

Current implementation must use:

```text
status=design_only_blocked
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

### 4. Operational runbook

This dry-run package may be built and validated as a design artifact only.

It must not be wired to:

```text
mail transport
external mail API send
recipient activation
PDF generation
delivery receipt creation
production delivery
```

## Recipient allowlist status

Allowed `recipient_allowlist_status` values for this design phase:

```text
not_configured
placeholder_only
configured_but_inactive
```

An active recipient allowlist is out of scope for this phase.

## Authority object

The `authority` object must explicitly preserve:

```text
mail_transport_configured=false
external_mail_api_enabled=false
send_function_present=false
recipient_activation=false
pdf_generation=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

## Blocking conditions

The artifact must contain blockers whenever delivery is not possible, including at least:

```text
email delivery dry-run only
send_attempted=false
recipient activation not enabled
mail sending out of scope
delivery receipt not created
production delivery disabled
```

Additional blockers must be present when WP9/WP11 artifacts are missing:

```text
delivery_manifest_status=not_available
pdf_status=not_available
```

## Current rule

WP12 may create the contract, builder, validator, tests and sample dry-run artifact.

WP12 must not:

```text
add mail transport configuration
send email
use external mail API sending
activate recipients
generate PDFs
create a real delivery receipt
claim production delivery
mutate portfolio state
promote candidates
wire dry-run output into the main workflow
```
