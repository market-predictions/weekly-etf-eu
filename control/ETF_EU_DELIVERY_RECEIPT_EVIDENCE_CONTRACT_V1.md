# ETF EU Delivery Receipt Evidence Contract V1

Date: 2026-07-11

## Purpose

Define redacted independent receipt evidence for a completed current-package transport run.

```text
upstream_pattern_adapted=weekly-etf manifest and run-closeout evidence concepts adapted for EU receipt verification
```

## Required inputs

```text
current-package transport result
current-package delivery evidence
independent receipt-source match
```

## Receipt rule

`receipt_confirmed=true` requires transport success plus an independent inbox match for the same report date and suffix, with the expected Dutch and English PDF and HTML attachments present.

## Stored metadata

Only hashes, timestamps, match flags, attachment booleans and status fields may be stored.

## Privacy boundary

```text
raw_email_content_stored=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

Transport success alone does not satisfy this contract.