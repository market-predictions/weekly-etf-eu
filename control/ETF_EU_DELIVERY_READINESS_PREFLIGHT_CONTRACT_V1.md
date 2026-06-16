# ETF EU Delivery Readiness Preflight Contract V1

## Purpose

This contract defines a deterministic readiness preflight artifact for a future Weekly ETF EU real delivery work package.

It is a **design-only readiness gate**. It does not enable SMTP, email sending, recipient activation, PDF generation, delivery receipts, production delivery, funding authority, portfolio mutation, candidate promotion or valuation-grade authority.

## Current readiness status

The current implementation must remain blocked:

```text
ready_for_wp13=false
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
pdf_generation=false
```

## Four-layer separation

### 1. Decision framework

The readiness preflight may decide whether prerequisites for a later delivery work package are present.

It is not a portfolio decision, fundability decision, pricing decision, candidate-promotion decision, send authorization or client-delivery proof.

### 2. Input/state contract

The readiness preflight may only inspect or reference prerequisite control paths:

```text
recipient allowlist
SMTP/secrets policy
delivery receipt validator
```

If these inputs are not provided, their status must be recorded as:

```text
recipient_allowlist_status=missing
smtp_secrets_policy_status=missing
delivery_receipt_validator_status=missing
```

A path being present in the artifact is not delivery authority.

### 3. Output contract

The readiness preflight artifact is a machine-readable control artifact under:

```text
output/delivery/etf_eu_delivery_readiness_preflight_<run_id>.json
```

Required top-level fields:

```text
schema_version
run_id
created_at_utc
report_date
status
ready_for_wp13
recipient_allowlist_status
recipient_allowlist_path_or_null
smtp_secrets_policy_status
smtp_secrets_policy_path_or_null
delivery_receipt_validator_status
delivery_receipt_validator_path_or_null
send_attempted
email_delivery
delivery_receipt
production_delivery
pdf_generation
funding_authority
portfolio_mutation
candidate_promotion
valuation_grade_promotion
authority
blockers
```

Allowed `schema_version`:

```text
etf_eu_delivery_readiness_preflight_v1
```

Allowed `status` values:

```text
blocked_not_ready_for_wp13
ready_for_wp13_preflight_only
```

Current sample artifact must use:

```text
status=blocked_not_ready_for_wp13
ready_for_wp13=false
```

### 4. Operational runbook

This package may build and validate the readiness preflight as a design artifact only.

It must not be wired to:

```text
mail transport
external mail API send
recipient activation
PDF generation
delivery receipt creation
production delivery
portfolio mutation
candidate promotion
```

## Prerequisite statuses

Allowed prerequisite status values:

```text
missing
present
```

The artifact may set a prerequisite to `present` only when a non-empty corresponding path is explicitly supplied.

The artifact may set `ready_for_wp13=true` only when all three prerequisite statuses are `present` and all three paths are non-empty.

Even when `ready_for_wp13=true`, all send, delivery, PDF, funding, portfolio and promotion authority flags must remain false.

## Required blocked artifact blockers

A blocked artifact must include at least:

```text
recipient allowlist not present
SMTP/secrets policy not present
delivery receipt validator not present
real delivery not authorized
```

If a prerequisite is later present, its missing blocker may be omitted, but `real delivery not authorized` must remain unless a future explicit delivery authority decision changes this contract.

## Authority fields

The artifact and nested `authority` object must explicitly preserve:

```text
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
pdf_generation=false
funding_authority=false
portfolio_mutation=false
candidate_promotion=false
valuation_grade_promotion=false
```

## Current rule

WP12B may create this contract, builder, validator, tests and sample blocked artifact.

WP12B must not:

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
wire this preflight into the main workflow
```
