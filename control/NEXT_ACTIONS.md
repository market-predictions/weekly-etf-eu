# Weekly ETF EU Review OS — Next Actions

Current priority: **RERUN_WORKFLOW_VALIDATE_ONLY — rerun ETF EU workflow with delivery_mode=validate_only**.

## Latest completion

```text
work_package_id=ETF-EU-MVP04-FIX-VALIDATE-ONLY-01
status=completed_output_contract_validator_hardening
source_work_package=ETF-EU-MVP04-FIX
failure_step=Validate EU output, pricing surface and fundability contracts
failure_reason=validator selected non-canonical legacy draft artifact before suffix filtering
unexpected_filename=weekly_etf_eu_review_260618_draft.md
fix_type=validator_selection_hardening
validator_updated=tools/validate_etf_eu_output_contract.py
regression_test_added=tests/test_etf_eu_output_contract_non_canonical_artifacts.py
non_canonical_eu_report_artifacts_ignored=true
canonical_report_suffix_filter_preserved=true
current_run_suffix_validation_preserved=true
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
Confirm that the output validator now ignores non-canonical legacy/draft report artifacts and validates only the current canonical report pair for the requested suffix.
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
