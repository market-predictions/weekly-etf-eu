# Weekly ETF EU Review OS — Next Actions

Current priority:

```text
RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT_WITH_CLIENT_GRADE_V2
```

## Production status

```text
workstream=ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2
status=promoted_to_routine_production
production_renderer=client_grade_v2
fresh_comparison_passed=true
promotion_smoke_passed=true
routine_production_ready=true
```

The v2 development and shadow-comparison lane is closed. Do not request another architecture promotion cycle unless a new concrete defect appears.

## Next routine cycle

Use:

```text
control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
.github/workflows/run-weekly-etf-eu-routine.yml
```

The next cycle must have:

```text
a new run_id
a new report_date
a new report_suffix
current UCITS pricing
current EU portfolio state
refreshed valuation history
current donor macro context adapted for EU descriptive use
ISIN-first instrument identity
Dutch-primary client-grade v2 output
English-companion client-grade v2 output
strict v2 validation
complete rendered-page review evidence
```

The routine path now performs:

```text
pricing refresh
→ macro adaptation
→ valuation-history refresh
→ normalized EU report state
→ investor brief and analyst appendix
→ conditional equity curve or cash-preservation surface
→ strict v2 validation
→ page-review evidence
→ existing production closeout path
```

## Equity surface

```text
portfolio_position_count=0
cash_eur=100000
current_equity_surface=cash_preservation_callout
```

Do not show a decorative flat graph. The equity curve activates automatically after meaningful validated NAV history or a funded position exists.

## Promotion evidence

```text
comparison_run_id=20260715_213100
comparison_workflow_run_id=29455916014
comparison_artifact_id=8359334286
comparison_blockers=0
promotion_recommended=true

smoke_run_id=20260715_224700
smoke_workflow_run_id=29456627922
smoke_artifact_id=8359605163
promoted_package_builder_passed=true
strict_v2_validation_passed=true
routine_v2_machine_gate_adapter_passed=true
visual_review_passed=true
production_action_performed=false
```

Decision record:

```text
control/decisions/ETF_EU_RPT01_CLIENT_GRADE_V2_PRODUCTION_PROMOTION_DECISION_20260716.md
```

## Closed identities

Do not reuse:

```text
source_run_id=20260712_125000
correction_control_id=20260713_180000
report_suffix=260712
preview_run_id=20260715_190000
comparison_run_id=20260715_213100
promotion_smoke_run_id=20260715_224700
```

## Development rule

Repair concrete defects directly in the promoted production path. Do not create new multi-stage architecture packages, repeated approval loops or parallel renderers for ordinary improvements.
