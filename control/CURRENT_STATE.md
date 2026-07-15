# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-15

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

## Active client-surface correction repair

```text
work_package_id=ETF-EU-RUN260712-FIX2A_CLIENT_SURFACE_SANITIZATION_BEFORE_RESEND
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
previous_repair_run_id=20260712_200000
previous_correction_control_id=20260713_000000
sanitization_run_id=20260713_180000
new_correction_control_id=20260713_180000
report_date=2026-07-12
report_suffix=260712
original_transport_success=true
original_client_output_valid=false
previous_corrected_package_superseded=true
previous_corrected_package_live_send_allowed=false
live_corrected_resend_allowed=false
sanitized_preview_generated=true
sanitized_preview_workflow_run_id=29416431004
sanitized_preview_workflow_job_id=87355635163
sanitized_preview_commit=af88817eadf2bccb60aa6fe677d34e2a35b97c7b
sanitized_preview_artifact_id=8343309423
client_surface_sanitization_passed=true
client_surface_clean=true
authority_separation_gate_passed=true
pdf_machine_gate_passed=true
visual_review_completed=true
visual_layout_gate_passed=true
client_surface_language_clean=true
pdf_visual_gate_passed=true
visual_language_blocker_count=0
dutch_pdf_page_count=3
english_pdf_page_count=3
pricing_line_count_detected=11
new_corrected_package_prepared=false
new_corrected_package_byte_identity_passed=false
new_dry_run_completed=false
correction_transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
client_surface_sanitizer_v2_created=true
client_surface_preview_workflow_v2_enabled=true
semantic_pricing_header_gate_created=true
status=sanitized_v2_preview_visual_approved_awaiting_validate_only
selected_next_action=RUN_SANITIZED_CORRECTION_PACKAGE_VALIDATE_ONLY
```

## Active FIX2A artifacts

```text
decision=control/decisions/ETF_EU_RUN260712_FIX2A_CLIENT_SURFACE_SANITIZATION_DECISION_20260713.md
supersession=output/delivery_control/etf_eu_corrected_resend_package_supersession_20260713_000000.json
sanitizer_v1=runtime/scrub_etf_eu_client_surface.py
sanitizer_v2=runtime/scrub_etf_eu_client_surface_v2.py
client_surface_validator=tools/validate_etf_eu_client_surface_clean.py
pdf_client_language_gate=tools/validate_etf_eu_routine_pdf_client_grade.py
authority_separation_validator=tools/validate_etf_eu_client_surface_authority_separation.py
preview_workflow=.github/workflows/repair-weekly-etf-eu-client-surface.yml
sanitized_dutch_pdf=output/repair_preview/20260713_180000/weekly_etf_eu_review_nl_260712.pdf
sanitized_english_pdf=output/repair_preview/20260713_180000/weekly_etf_eu_review_260712.pdf
combined_machine_gate=output/quality/etf_eu_routine_pdf_client_grade_20260713_180000.json
visual_review=output/quality/etf_eu_routine_pdf_visual_review_20260713_180000.json
authority_separation=output/quality/etf_eu_client_surface_authority_separation_20260713_180000.json
new_queue=control/run_queue/etf_eu_corrected_resend_request_20260713_180000.md
new_package_manifest=output/delivery_control/etf_eu_corrected_resend_package_20260713_180000.json
```

## Passed v2 client-output gates

```text
Dutch client-surface clean=true
English client-surface clean=true
Dutch semantic pricing header=Handelslijn / Peildatum
English semantic pricing header=Trading line / Pricing date
raw status enums absent=true
authority and transport metadata absent=true
sections 1-7 complete=true
section 8 absent=true
Dutch PDF pages=3
English PDF pages=3
pricing lines represented=11
visual_review_passed=true
blockers=[]
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
original_transport_evidence_overwritten=false
weekly_etf_eu_source_of_truth=true
weekly_etf_upstream_donor_only=true
```

## Current note

Workflow run `29416431004` completed successfully. Sanitizer v2, Dutch and English client-surface validation, semantic PDF language validation, authority separation, page rendering, artifact upload and persistence all passed. All six first, middle and last page renders were inspected and the visual-review artifact was approved with no blockers. The next action is to run the generalized corrected-report workflow in `validate_only` mode for correction control id `20260713_180000`. No correction transport or receipt check has occurred.
