# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-13

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Latest completed production cycle

```text
work_package_id=ETF-EU-MVP30_PRODUCTION_DELIVERY_CLOSEOUT_AND_ROUTINE_RUNBOOK
status=completed_production_delivery_closeout
run_id=20260710_000000
runtime_run_id=20260711_175327
report_date=2026-07-10
transport_success=true
receipt_confirmed_from_new_run=true
production_delivery_cycle_closed=true
routine_production_ready=true
operating_mode=routine_production
```

## Active routine run and corrected-output repair

```text
work_package_id=ETF-EU-RUN260712-FIX1_CLIENT_GRADE_PDF_RENDERER_REPAIR
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
routine_run_id=20260712_125000
runtime_run_id=20260712_182002
report_date=2026-07-12
report_suffix=260712
fresh_package_committed=true
send_executed=true
transport_attempted=true
transport_success=true
receipt_confirmed=false
original_client_output_valid=false
original_pdf_client_grade=false
production_delivery_complete=false
defect=routine_pdf_renderer_plain_text_single_page_clipping
defect_artifact=output/quality/etf_eu_routine_output_defect_20260712_182002.json
original_dutch_pdf=output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf
original_english_pdf=output/fresh_generation/weekly_etf_eu_review_260712.pdf
repair_run_id=20260712_200000
repair_workflow=.github/workflows/repair-weekly-etf-eu-routine-pdf.yml
repair_workflow_run_id=29246566901
repair_workflow_artifact_id=8277605032
renderer_repair_implemented=true
machine_validator_created=true
rendered_page_review_helper_created=true
normal_routine_workflow_hardened=true
preview_attempt_count=3
latest_preview_attempt_status=success
corrected_preview_generated=true
corrected_dutch_pdf=output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.pdf
corrected_english_pdf=output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.pdf
corrected_dutch_page_count=3
corrected_english_page_count=3
corrected_pdf_machine_gate_passed=true
corrected_pdf_visual_gate_passed=true
corrected_client_output_valid=true
transport_attempted_for_correction=false
corrected_resend_executed=false
corrected_resend_pending=true
status=completed_renderer_repair_preview_and_visual_review
selected_next_action=PREPARE_EXPLICIT_CORRECTED_REPORT_RESEND
```

## Authority and privacy boundaries

```text
portfolio_action=no_transaction
cash_eur=100000
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
raw_receipt_pdf_stored_in_github=false
weekly_etf_eu_source_of_truth=true
weekly_etf_upstream_donor_only=true
```

## Current note

The original `2026-07-12` transport remains SMTP-success evidence only because its plain-text PDFs failed the client output contract. The corrected Dutch and English previews were generated in GitHub Actions run `29246566901`, passed both machine gates, and passed explicit first/middle/last-page visual review. No correction transport or receipt check occurred. The next step is a separate explicit corrected-resend package using the approved repair-preview artifacts.
