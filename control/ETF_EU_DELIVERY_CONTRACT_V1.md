# ETF EU Delivery Contract V1

## Purpose

This contract defines the delivery manifest and receipt contract for the Weekly ETF EU report system.

It is a **design-only delivery enablement contract**. It does not enable email, PDF generation, SMTP, recipient handling, or production delivery.

## Current delivery status

```text
delivery_enabled=false
production_delivery=false
pdf_generation=false
email_delivery=false
delivery_receipt=false
```

## Four-layer separation

### 1. Decision framework

Delivery may only publish an already validated Dutch-first EU report. Delivery is not a portfolio decision, pricing decision, fundability decision, or candidate-promotion mechanism.

### 2. Input/state contract

A delivery manifest may reference only already produced and validated artifacts:

```text
output/weekly_etf_eu_review_*.md
output/weekly_etf_eu_review_nl_*.md
output/pricing/ucits_valuation_prices_*.json
output/validation/*.json
```

It must not create or change portfolio state.

### 3. Output contract

A delivery manifest is a machine-readable control artifact under:

```text
output/delivery/etf_eu_delivery_manifest_<run_id>.json
```

A delivery receipt, when delivery is later implemented, must be a separate machine-readable artifact under:

```text
output/delivery/etf_eu_delivery_receipt_<run_id>.json
```

A manifest is not a receipt. A queued, blocked, or design-only manifest must not be described as delivered.

### 4. Operational runbook

A future delivery workflow may run only after all gates below pass:

```text
main_workflow_green=true
dutch_first_report_contract_green=true
fundability_rules_clear=true
delivery_manifest_exists=true
receipt_path_exists=true
```

Until then, delivery remains blocked.

## Manifest schema

Required top-level fields:

```text
schema_version
run_id
created_at_utc
report_date
status
delivery_enabled
gates
artifacts
receipt
authority
blockers
```

Allowed `schema_version`:

```text
etf_eu_delivery_manifest_v1
```

Allowed `status` values:

```text
blocked_design_only
ready_for_future_delivery
sent
failed
```

Current implementation must use:

```text
status=blocked_design_only
delivery_enabled=false
```

## Required gates

The `gates` object must include:

```text
main_workflow_green
dutch_first_report_contract_green
fundability_rules_clear
delivery_manifest_exists
receipt_path_exists
```

Current design-only manifests may set `delivery_manifest_exists=true` because the manifest itself exists, but must keep `delivery_enabled=false` unless every gate is true and a later delivery implementation explicitly authorizes delivery.

## Required artifacts

The `artifacts` object must include:

```text
dutch_report_path
english_report_path
valuation_artifact_path
validation_evidence_paths
```

The Dutch report path is the primary client-facing artifact. The English report path is companion/operator-facing unless a later decision changes this.

## Receipt contract

The `receipt` object must include:

```text
receipt_required
receipt_path
receipt_status
```

Allowed `receipt_status` values:

```text
not_created
pending
created
failed
```

For any manifest with `status=sent`, the receipt must prove delivery and must include a non-empty `receipt_path`.

## Authority object

The `authority` object must explicitly preserve:

```text
funding_authority=false
portfolio_mutation=false
valuation_grade_promotion=false
candidate_promotion_to_fundable=false
pdf_generation=false
email_delivery=false
production_delivery=false
```

A future real delivery manifest may set `pdf_generation`, `email_delivery`, or `production_delivery` differently only after a separate delivery implementation and decision log entry.

## Blocking conditions

Delivery remains blocked if any of these are true:

```text
main workflow not green
Dutch-first report contract not green
fundability rules unclear
manifest missing
receipt path missing
delivery_enabled=false
production_delivery=false
email/PDF implementation not explicitly authorized
```

## Current rule

WP8 may create the contract, validator, manifest helper and tests.

WP8 must not:

```text
enable SMTP
send email
render PDF
claim delivery success
create a real delivery receipt
mutate portfolio state
promote candidates
switch workflow delivery behavior
```
