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
ETF-EU-MVP04-FIX-VALIDATE-ONLY-02
```

## Latest completed package — ETF-EU-MVP04-FIX-VALIDATE-ONLY-02

```text
repository=market-predictions/weekly-etf-eu
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
selected_next_package_title=Rerun ETF EU workflow with delivery_mode validate_only
```

## Previous validate-only fix — ETF-EU-MVP04-FIX-VALIDATE-ONLY-01

```text
validator_updated=tools/validate_etf_eu_output_contract.py
regression_test_added=tests/test_etf_eu_output_contract_non_canonical_artifacts.py
non_canonical_eu_report_artifacts_ignored=true
canonical_report_suffix_filter_preserved=true
current_run_suffix_validation_preserved=true
```

## Validate-only candidate report fix answer

```text
The validate_only workflow next failed because tools/validate_etf_eu_candidate_report.py selected historical and non-canonical report artifacts, including weekly_etf_eu_review_260618_draft.md. The candidate report validator now ignores non-canonical EU report artifacts and, when no suffix is supplied, validates only the latest canonical Dutch/English report pair. It also supports an explicit report suffix if needed. No legacy artifact was deleted and no delivery action was performed.
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
