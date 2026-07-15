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
sanitized_preview_commit=f0d07ac7ec2ede1825cc868f162b45d7060ad7b6
client_surface_sanitization_passed=true
authority_separation_gate_passed=true
pdf_machine_gate_passed=true
visual_review_completed=true
visual_layout_gate_passed=true
client_surface_language_clean=false
pdf_visual_gate_passed=false
visual_language_blocker_count=3
latest_corrected_resend_workflow_run_id=29411450220
latest_corrected_resend_job_id=87339249817
latest_corrected_resend_attempt_status=blocked_before_package_preparation
latest_corrected_resend_failure=visual_review_did_not_pass
new_corrected_package_prepared=false
new_corrected_package_byte_identity_passed=false
new_dry_run_completed=false
correction_transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
client_surface_sanitizer_v2_created=true
client_surface_preview_workflow_v2_enabled=true
semantic_pricing_header_gate_created=true
status=visual_review_failed_language_contract_awaiting_v2_preview
selected_next_action=RERUN_CLIENT_SURFACE_REPAIR_PREVIEW_WITH_V2
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

## Confirmed visual-language blockers in superseded preview

```text
1. Dutch pricing table used the English header Trading line and labelled the pricing-date column as Markt.
2. Dutch decision copy contained broker- en bevestiging van de handelslijn.
3. Dutch risk copy contained afzonderlijke afzonderlijk besluit.
```

The page layout, pagination, tables, headings and Unicode passed. The preview did not pass the complete visual contract because client language is part of the visual/client-grade gate.

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

Corrected-resend workflow run `29411450220`, job `87339249817`, was correctly blocked in package preparation because the visual-review artifact had not passed. Validate-only, dry-run, authorization and send were skipped. Manual inspection then confirmed clean layout but three Dutch client-language defects. Sanitizer v2, the preview workflow and the semantic PDF language gate have been updated. Start a new client-surface repair preview from current `main`; do not rerun the failed corrected-resend job and do not attempt transport.
