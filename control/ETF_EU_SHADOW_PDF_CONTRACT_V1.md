# ETF EU Shadow PDF Contract V1

## Purpose

This contract defines a **shadow-only** PDF rendering path for the Weekly ETF EU Dutch-first report pair.

It prepares PDF artifact generation for later operational maturity, but it does **not** enable production delivery, email delivery, SMTP, recipient configuration, or delivery receipts.

## Current shadow PDF status

```text
pdf_generation=shadow_only
production_delivery=false
email_delivery=false
delivery_receipt=false
```

The current implementation may render local/shadow PDF files only. A rendered PDF is not a delivery receipt and must not be described as production delivery.

## Four-layer separation

### 1. Decision framework

PDF rendering is a format-conversion step only. It must not create a portfolio decision, pricing decision, fundability decision, candidate-promotion decision, or client delivery decision.

The rendered PDFs inherit the authority status of the already-rendered Markdown reports. PDF rendering cannot upgrade a report from shadow/bootstrap/non-delivered status to delivered status.

### 2. Input/state contract

The shadow renderer may read only already-produced Markdown report artifacts:

```text
output/weekly_etf_eu_review_nl_<date>.md
output/weekly_etf_eu_review_<date>.md
```

It must not read, create, or mutate portfolio state, pricing state, recipient configuration, SMTP credentials, or delivery receipts.

### 3. Output contract

The renderer may write only local/shadow PDF artifacts under:

```text
output/pdf/weekly_etf_eu_review_nl_<date>.pdf
output/pdf/weekly_etf_eu_review_<date>.pdf
```

The renderer may also write a machine-readable shadow manifest under:

```text
output/pdf/etf_eu_shadow_pdf_manifest_<run_id>.json
```

Required manifest authority fields:

```text
pdf_generation=shadow_only
production_delivery=false
email_delivery=false
delivery_receipt=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
candidate_promotion=false
```

The Dutch PDF remains the primary client-facing rendering candidate. The English PDF remains companion/operator-facing.

### 4. Operational runbook

This work package may add:

```text
contract text
renderer helper or deterministic stub
validator
tests
```

It must not wire PDF rendering into the main workflow until the delivery manifest operational integration is complete and a later work package explicitly authorizes workflow integration.

## Required behavior

The shadow renderer must:

1. resolve the same date suffix as the Markdown report pair;
2. render or stub deterministic PDF files for both Dutch and English Markdown reports;
3. keep all delivery flags false;
4. mark `pdf_generation` as `shadow_only` rather than production-enabled;
5. write outputs only under `output/pdf/` unless a test/output directory is explicitly provided;
6. never claim delivery completion.

## Validator expectations

The validator must confirm:

```text
schema_version=etf_eu_shadow_pdf_manifest_v1
pdf_generation=shadow_only
production_delivery=false
email_delivery=false
delivery_receipt=false
```

It must also confirm that referenced PDF files exist, have `.pdf` suffixes, are inside the configured PDF output directory, and start with a PDF header.

## Hard prohibitions

WP11 must not add:

```text
email delivery
SMTP
recipient config
delivery receipt
production delivery claim
portfolio mutation
funding authority
valuation-grade promotion
candidate promotion
main workflow PDF integration
```

## Integration gate

Shadow PDF rendering remains design/test-only until WP9 delivery manifest operational integration is complete and a later authority decision explicitly permits workflow integration.
