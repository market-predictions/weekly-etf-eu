# Weekly ETF EU Review OS — Next Actions

The repository now has two synchronized priorities:

```text
operational_priority=RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT
development_priority=RUN_FRESH_CURRENT_DATE_V2_SHADOW_AND_DECIDE_PROMOTION
```

## Closed correction cycle

```text
work_package_id=ETF-EU-RUN260712-FIX2B_CORRECTED_RESEND_RECEIPT_CLOSEOUT
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
correction_control_id=20260713_180000
repair_run_id=20260713_180000
transport_runtime_run_id=20260715_152543
github_workflow_run_id=29428021408
report_date=2026-07-12
report_suffix=260712
corrected_resend_executed=true
correction_transport_success=true
receipt_confirmed=true
expected_attachment_set_seen=true
attachment_count_seen=4
production_delivery_cycle_closed=true
routine_production_ready=true
additional_resend_required=false
operating_mode=routine_production
```

Do not rerun or reuse this correction cycle. These identities and artifacts are closed historical evidence.

## Completed client-grade v2 development stream

```text
workstream=ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2
preview_run_id=20260715_190000
workflow_run_id=29442173869
workflow_conclusion=success
artifact_id=8353893752
strict_validation_passed=true
validation_blockers=0
dutch_page_count=6
english_page_count=6
all_pages_visually_reviewed=true
visual_review_passed=true
production_renderer_replaced=false
production_delivery_performed=false
```

Completed capabilities:

```text
premium investor brief
premium analyst appendix
normalized EU report state
macro and policy dashboard
structural UCITS opportunity radar
risk and invalidation surface
allocation map
second-order effects
UCITS pricing and identity appendix
verification funnel
conditional position and rotation sections
valuation-history updater
conditional deterministic equity curve
cash-preservation fallback
Dutch and English component renderer
bilingual polish layer
strict client-grade validator
single preview workflow
```

Evidence:

```text
control/evidence/ETF_EU_RPT01_CLIENT_GRADE_V2_PREVIEW_EVIDENCE_20260715.md
docs/roadmaps/WEEKLY_ETF_EU_CLIENT_GRADE_REPORT_ROADMAP_20260715.md
```

## Exact operational next action

Start the next normal routine Weekly ETF EU cycle under:

```text
control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
```

Use:

```text
a new run_id
a new report_date
a new report_suffix
current pricing
current EU portfolio state
current macro evidence
ISIN-first instrument authority
Dutch-primary and English-companion outputs
guarded delivery
delayed independent receipt verification
```

## Exact development next action

After that fresh routine cycle has produced current state, pricing and macro artifacts, run the existing workflow once:

```text
Workflow: Weekly ETF EU client-grade v2 preview
preview_run_id: <new unique preview id>
source_run_id: <new routine run id>
report_date: <new routine report date>
report_suffix: <new routine report suffix>
pricing_artifact: <fresh routine pricing artifact>
```

This is a shadow render only. It performs no portfolio mutation and no delivery.

Required outcome:

```text
strict client-grade validation passes
fresh macro warning is absent
Dutch and English visual review passes
equity curve or cash-preservation surface is truthful
production and v2 report use the same current state and pricing authority
```

If that one fresh shadow comparison passes, make one explicit decision:

```text
PROMOTE_CLIENT_GRADE_V2_TO_ROUTINE_PRODUCTION
```

Do not create six new work packages, repeated approval gates or another architecture roadmap. Repair only concrete defects found in the fresh shadow comparison.

## Closed identities that must not be reused

```text
source_run_id=20260712_125000
correction_control_id=20260713_180000
transport_runtime_run_id=20260715_152543
report_suffix=260712
preview_run_id=20260715_190000
```
