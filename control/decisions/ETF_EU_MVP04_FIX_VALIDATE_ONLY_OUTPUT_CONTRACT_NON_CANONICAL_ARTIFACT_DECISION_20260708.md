# ETF-EU-MVP04-FIX validate-only output contract non-canonical artifact decision — 2026-07-08

## Decision

Harden the ETF EU output contract validator so non-canonical legacy/draft report artifacts are ignored before suffix selection.

## Failure

```text
step=Validate EU output, pricing surface and fundability contracts
command=python tools/validate_etf_eu_output_contract.py --output-dir output --require-production-dutch-first --report-suffix $ETF_EU_REPORT_SUFFIX
unexpected_filename=weekly_etf_eu_review_260618_draft.md
```

## Root cause

```text
The validator globbed weekly_etf_eu_review*.md and called _report_suffix on every match. A legacy draft artifact matched the broad prefix but not the canonical EU report filename contract, so suffix selection failed before the current run's canonical report pair could be validated.
```

## Fix

```text
validator_updated=tools/validate_etf_eu_output_contract.py
regression_test_added=tests/test_etf_eu_output_contract_non_canonical_artifacts.py
non_canonical_eu_report_artifacts_ignored=true
canonical_report_suffix_filter_preserved=true
current_run_suffix_validation_preserved=true
```

## Boundaries

```text
legacy_draft_artifact_deleted=false
production_delivery=false
send_performed=false
email_delivery=false
delivery_success_claimed=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
pricing_evidence_changed=false
source_pdf_replaced=false
new_pdf_created=false
renderer_changed=false
```

## Next step

```text
RERUN_WORKFLOW_VALIDATE_ONLY
```
