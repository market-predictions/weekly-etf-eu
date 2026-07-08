# ETF-EU-MVP04-FIX validate-only candidate report selection decision — 2026-07-08

## Decision

Harden the ETF EU candidate report validator so it ignores non-canonical legacy/draft artifacts and validates the latest canonical report pair by default.

## Failure

```text
step=Validate EU output, pricing surface and fundability contracts
command=python tools/validate_etf_eu_candidate_report.py --output-dir output
unexpected_filename=weekly_etf_eu_review_260618_draft.md
```

## Root cause

```text
The candidate report validator globbed weekly_etf_eu_review*.md and validated every match. Historical canonical reports and non-canonical draft artifacts were included even though the workflow only needs to validate the current report pair.
```

## Fix

```text
validator_updated=tools/validate_etf_eu_candidate_report.py
regression_test_added=tests/test_etf_eu_candidate_report_selection.py
non_canonical_eu_report_artifacts_ignored=true
latest_canonical_pair_default_selection=true
optional_report_suffix_filter_added=true
current_run_suffix_validation_supported=true
```

## Boundaries

```text
legacy_draft_artifact_deleted=false
production_delivery=false
workflow_message_sent=false
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
