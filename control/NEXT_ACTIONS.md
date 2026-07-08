# Weekly ETF EU Review OS — Next Actions

Current priority: **RERUN_WORKFLOW_VALIDATE_ONLY — rerun ETF EU workflow with delivery_mode=validate_only**.

## Latest completion

```text
work_package_id=ETF-EU-MVP04-FIX-VALIDATE-ONLY-02
status=completed_candidate_report_selection_hardening
source_work_package=ETF-EU-MVP04-FIX-VALIDATE-ONLY-01
failure_step=Validate EU output, pricing surface and fundability contracts
failure_reason=candidate report validator selected historical and non-canonical report artifacts instead of current canonical pair
unexpected_filename=weekly_etf_eu_review_260618_draft.md
fix_type=candidate_report_selection_hardening
validator_updated=tools/validate_etf_eu_candidate_report.py
regression_test_added=tests/test_etf_eu_candidate_report_selection.py
non_canonical_eu_report_artifacts_ignored=true
latest_canonical_pair_default_selection=true
optional_report_suffix_filter_added=true
current_run_suffix_validation_supported=true
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
selected_next_package=RERUN_WORKFLOW_VALIDATE_ONLY
```

## Active next step

```text
RERUN_WORKFLOW_VALIDATE_ONLY — rerun ETF EU workflow with delivery_mode=validate_only
```

Purpose:

```text
Confirm that both EU report validators now ignore non-canonical legacy/draft report artifacts and validate only the current canonical report pair.
```

## Operator instructions

In GitHub Actions, rerun:

```text
Weekly ETF EU UCITS rolemodel delivery workflow
```

Choose:

```text
delivery_mode=validate_only
```

If that workflow is green, run again with:

```text
delivery_mode=dry_run
```

Do not choose:

```text
delivery_mode=send
```

until an EU-specific sender entrypoint has been explicitly validated.

## Scope guardrails

```text
Do not fill manual operator evidence/hash reference templates for delivery.
Do not open ETF-EU-MVP05 merely to ask for the same values again.
Do not return to WP15 abstract authority gates unless a concrete validator failure occurs.
Do not fetch new close prices outside the workflow run.
Do not mutate portfolio state.
Do not create valuation-grade authority.
Do not create funding authority.
Do not create funded positions.
Do not change recommendation logic in production.
Do not claim delivery success without a real delivery manifest or receipt.
Do not expose private runtime values.
Do not expose recipient values.
```
