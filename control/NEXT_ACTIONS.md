# Weekly ETF EU Review OS — Next Actions

Current priority: **COMPLETE_RUN260712_PDF_REPAIR_AND_VISUAL_REVIEW**.

## Active defect repair

```text
work_package_id=ETF-EU-RUN260712-FIX1_CLIENT_GRADE_PDF_RENDERER_REPAIR
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
report_date=2026-07-12
report_suffix=260712
original_transport_success=true
original_client_output_valid=false
repair_run_id=20260712_200000
repair_workflow=.github/workflows/repair-weekly-etf-eu-routine-pdf.yml
preview_attempt_count=2
latest_preview_machine_gate_passed=true
latest_preview_review_pages_rendered=true
latest_preview_artifacts_persisted=false
latest_preview_failure=decision_log_inline_heredoc_syntax_error
latest_preview_failure_repaired=true
workflow_fix_commit=5c09433c1327763290351a2ea20837fc44c5bbfd
corrected_preview_generated=false
corrected_resend_executed=false
receipt_confirmed=false
```

## Exact next action

Start a new GitHub Actions workflow run from current `main`. Do not use **Re-run failed jobs**, because that would execute the historical workflow commit.

```text
Repository: market-predictions/weekly-etf-eu
Workflow: Weekly ETF EU routine PDF repair preview
Branch: main
source_run_id: 20260712_125000
repair_run_id: 20260712_200000
report_suffix: 260712
```

The workflow is preview-only. It contains no mail secrets, transport runner or receipt checker. The nonessential inline decision-log step has been removed; stable decisions remain maintained directly in GitHub control files and decision artifacts.

## Required review sequence

```text
1. run Weekly ETF EU routine PDF repair preview from current main
2. verify Dutch and English machine-gate artifacts are committed
3. inspect Dutch first, middle and last rendered pages
4. inspect English first, middle and last rendered pages
5. confirm no right-edge or bottom clipping
6. confirm no overlapping text
7. confirm tables, headings and Dutch Unicode are readable
8. confirm sections 1-8 and the authority block are visible
9. update the visual-review artifact only after actual inspection
10. do not resend in FIX1
11. prepare an explicit corrected-resend package only after both gates pass
```

## Expected preview outputs

```text
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.pdf
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.pdf
output/repair_preview/20260712_200000/pages/nl/
output/repair_preview/20260712_200000/pages/en/
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000.json
output/quality/etf_eu_routine_pdf_visual_review_20260712_200000.json
```

## Delivery boundary

```text
send_or_resend_allowed=false
correction_transport_allowed=false
receipt_check_allowed=false
production_delivery_complete=false
```

The next action after passed machine and visual review is:

```text
PREPARE_EXPLICIT_CORRECTED_REPORT_RESEND
```

Do not create MVP31. Keep `weekly-etf-eu` as EU authority and use `weekly-etf` only for mature renderer, validation and delivery-control concepts.
