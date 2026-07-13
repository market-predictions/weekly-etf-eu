# Weekly ETF EU Review OS — Next Actions

Current priority: **PREPARE_EXPLICIT_CORRECTED_REPORT_RESEND**.

## Completed repair evidence

```text
work_package_id=ETF-EU-RUN260712-FIX1_CLIENT_GRADE_PDF_RENDERER_REPAIR
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
report_date=2026-07-12
report_suffix=260712
original_transport_success=true
original_client_output_valid=false
repair_run_id=20260712_200000
repair_workflow_run_id=29246566901
repair_workflow_artifact_id=8277605032
corrected_preview_generated=true
corrected_dutch_page_count=3
corrected_english_page_count=3
corrected_pdf_machine_gate_passed=true
corrected_pdf_visual_gate_passed=true
corrected_client_output_valid=true
corrected_resend_executed=false
receipt_confirmed=false
```

## Approved corrected outputs

```text
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.pdf
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.pdf
```

Machine evidence:

```text
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000_nl.json
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000_en.json
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000.json
```

Visual evidence:

```text
output/quality/etf_eu_routine_pdf_visual_review_20260712_200000.json
```

## Exact next action

Create a narrow corrected-resend package that:

```text
1. uses only the approved repair-preview Dutch and English HTML/PDF files
2. preserves the original report date and analysis content
3. labels the transport as a corrected resend
4. requires explicit guarded-send selection
5. writes new correction transport and delivery-evidence artifacts
6. does not overwrite the original transport evidence
7. keeps receipt_confirmed=false until independent receipt evidence exists
8. performs delayed receipt verification after successful corrected transport
```

Do not reuse the malformed original PDFs.

Do not run the normal routine generation workflow again for this correction.

Do not create MVP31. Use a narrow run-specific corrected-resend package.

## Current delivery boundary

```text
corrected_resend_allowed_for_preparation=true
corrected_resend_execution_allowed=false until explicit guarded selection
correction_transport_attempted=false
corrected_resend_executed=false
receipt_check_allowed=false until correction transport succeeds
production_delivery_complete=false
```

Recommended next package:

```text
ETF-EU-RUN260712-FIX2_EXPLICIT_CORRECTED_REPORT_RESEND
```

Keep `weekly-etf-eu` as EU authority and inspect `weekly-etf` first for mature corrected-delivery and evidence concepts before implementing FIX2.
