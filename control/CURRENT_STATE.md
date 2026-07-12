# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-12

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

## Active routine run and output defect

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
client_output_valid=false
pdf_client_grade=false
production_delivery_complete=false
defect=routine_pdf_renderer_plain_text_single_page_clipping
defect_artifact=output/quality/etf_eu_routine_output_defect_20260712_182002.json
original_dutch_pdf=output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf
original_english_pdf=output/fresh_generation/weekly_etf_eu_review_260712.pdf
repair_run_id=20260712_200000
repair_workflow=.github/workflows/repair-weekly-etf-eu-routine-pdf.yml
renderer_repair_implemented=true
machine_validator_created=true
rendered_page_review_helper_created=true
normal_routine_workflow_hardened=true
preview_attempt_count=2
latest_preview_attempt_status=failed_after_machine_validation_and_review_page_rendering
latest_preview_failure=decision_log_inline_heredoc_syntax_error
latest_preview_failure_repaired=true
latest_preview_fix_commit=5c09433c1327763290351a2ea20837fc44c5bbfd
corrected_preview_generated=false
corrected_pdf_machine_gate_passed=false
corrected_pdf_visual_gate_passed=false
transport_attempted_for_correction=false
corrected_resend_executed=false
corrected_resend_pending=true
status=renderer_repair_implemented_awaiting_preview_rerun
selected_next_action=RUN_CLIENT_GRADE_PDF_REPAIR_PREVIEW_FROM_CURRENT_MAIN
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

The `2026-07-12` routine workflow completed SMTP transport, but the original plain-text PDF renderer produced materially incomplete client output. SMTP success is preserved as transport evidence while production delivery completion remains false. The repair renderer, PDF machine gate and review-page rendering now execute successfully. The latest preview attempt failed only in a nonessential inline decision-log step after those gates completed. That brittle step has been removed from the workflow. Start a new preview run from current `main`; do not use the historical failed run, resend the report or check receipt.
