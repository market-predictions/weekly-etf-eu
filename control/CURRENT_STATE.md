# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-08

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Current phase

```text
Phase 9 — EU product assembly via donor-port strategy
```

## Core boundary

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
```

## Strategic authority

`weekly-etf-eu` remains the EU/UCITS source-of-truth repo. `weekly-etf` remains a donor for mature implementation patterns only.

```text
Port behavior, not U.S. assumptions.
```

## Closed packages

```text
ETF-EU-WP15V
ETF-EU-WP15W
ETF-EU-WP15X
ETF-EU-WP15Y
ETF-EU-WP15Y-FIX
ETF-EU-WP15Z
ETF-EU-WP15AA
ETF-EU-WP15AA-FIX
ETF-EU-WP15AB
ETF-EU-WP15AC
ETF-EU-WP15AD
ETF-EU-WP15AE
ETF-EU-WP15AF
ETF-EU-WP15AG
ETF-EU-WP15AH
ETF-EU-WP15AI
ETF-EU-WP15AJ
ETF-EU-WP15AK
ETF-EU-WP15AL
ETF-EU-WP15AM
ETF-EU-WP15AN
ETF-EU-WP15AO
ETF-EU-WP15AP
ETF-EU-WP15AQ
ETF-EU-MVP01
ETF-EU-MVP02
ETF-EU-MVP03
ETF-EU-MVP04
ETF-EU-MVP04-FIX
ETF-EU-MVP04-FIX-VALIDATE-ONLY-01
```

## Latest completed package — ETF-EU-MVP04-FIX-VALIDATE-ONLY-01

```text
repository=market-predictions/weekly-etf-eu
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
selected_next_package_title=Rerun ETF EU workflow with delivery_mode validate_only
```

## Previous completed package — ETF-EU-MVP04-FIX

```text
manual_evidence_route_superseded=true
operator_reference_template_required_for_delivery=false
operator_hash_requirement_removed=true
workflow_delivery_mode_input_created=true
delivery_mode_default=validate_only
delivery_mode_options=validate_only,dry_run,send
push_delivery_mode=validate_only
dry_run_mode_declared=true
send_mode_declared=true
send_mode_blocked_until_eu_sender_validated=true
rolemodel_secret_names_declared=true
delivery_workflow_alignment_status=rolemodel_gated_safe_default
delivery_execution_status=validate_only_or_dry_run_ready
send_execution_status=blocked_pending_eu_sender_entrypoint_validation
selected_next_package=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN
```

## Validate-only failure fix answer

```text
The validate_only workflow failed because tools/validate_etf_eu_output_contract.py selected a non-canonical legacy draft artifact, weekly_etf_eu_review_260618_draft.md, before applying the current run suffix filter. The validator now ignores non-canonical EU report artifacts with a warning and validates only canonical report filenames for the requested suffix. No legacy artifact was deleted and no delivery action was performed.
```

## Active product roadmap

```text
RERUN_WORKFLOW_VALIDATE_ONLY — rerun ETF EU workflow with delivery_mode=validate_only
```

## Immediate next action

In GitHub Actions, rerun:

```text
Weekly ETF EU UCITS rolemodel delivery workflow
```

Choose:

```text
delivery_mode=validate_only
```

If green, run again with:

```text
delivery_mode=dry_run
```

Do not use `delivery_mode=send` until an EU-specific sender entrypoint has been explicitly validated.
