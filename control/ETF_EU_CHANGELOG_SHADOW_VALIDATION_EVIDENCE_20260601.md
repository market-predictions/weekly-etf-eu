# Changelog — Shadow Validation Evidence Artifact

Date: 2026-06-01
Repository: `market-predictions/weekly-etf-eu`
Scope: repo-native validation evidence for future ChatGPT verification.

## Current issue

GitHub Actions run visibility is not always available through ChatGPT connector tools. Future chats need a durable, repo-native way to verify that a bootstrap validation run passed without relying on the Actions UI.

## Change

Added a non-production shadow validation evidence mechanism.

## Files added

```text
tools/build_etf_eu_shadow_validation_evidence.py
tools/validate_etf_eu_shadow_validation_evidence.py
```

## File changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

## Output artifact

The workflow now writes:

```text
output/validation/etf_eu_shadow_validation_evidence_YYYYMMDD_HHMMSS.json
```

This file is committed back to GitHub with the other bootstrap artifacts.

## Safety rules

The evidence artifact is not a production delivery receipt. It explicitly keeps:

```text
production_delivery=false
portfolio_mutation=false
funding_authority=false
valuation_authority=false
email_delivery=false
pdf_render=false
delivery_receipt=false
not_delivery_receipt=true
shadow_validation_only=true
```

The validator checks the schema, required artifact list, hashes, false authority flags and safety-check metadata.

## Purpose

Future chats can verify a completed bootstrap run directly from GitHub by reading the latest file in `output/validation/`, instead of depending on Actions UI visibility.

## Authority impact

No valuation, funding, portfolio mutation, PDF rendering or email delivery authority was added.
