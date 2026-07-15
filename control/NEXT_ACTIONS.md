# Weekly ETF EU Review OS — Next Actions

Current priority: **RUN_SANITIZED_CORRECTION_PACKAGE_VALIDATE_ONLY**.

## Active package

```text
work_package_id=ETF-EU-RUN260712-FIX2A_CLIENT_SURFACE_SANITIZATION_BEFORE_RESEND
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
previous_correction_control_id=20260713_000000
sanitization_run_id=20260713_180000
new_correction_control_id=20260713_180000
report_date=2026-07-12
report_suffix=260712
previous_corrected_package_superseded=true
previous_corrected_package_live_send_allowed=false
live_corrected_resend_allowed=false
sanitized_preview_workflow_run_id=29416431004
sanitized_preview_workflow_job_id=87355635163
sanitized_preview_commit=af88817eadf2bccb60aa6fe677d34e2a35b97c7b
client_surface_sanitization_passed=true
client_surface_clean=true
authority_separation_gate_passed=true
pdf_machine_gate_passed=true
pdf_visual_gate_passed=true
client_surface_language_clean=true
visual_review_passed=true
visual_review_blockers=[]
new_corrected_package_prepared=false
new_corrected_package_byte_identity_passed=false
new_dry_run_completed=false
correction_transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
```

## Verified v2 preview result

```text
Dutch PDF pages=3
English PDF pages=3
pricing lines represented=11
Dutch headers=Handelslijn / Peildatum
English headers=Trading line / Pricing date
sections 1-7 complete=true
section 8 absent=true
raw status enums absent=true
authority and transport metadata absent=true
no clipping=true
no overlap=true
tables readable=true
headings readable=true
Dutch Unicode correct=true
client language clean=true
duplicate title absent=true
```

## Exact next action — validate only

Start a fresh GitHub Actions run from current `main`:

```text
Repository: market-predictions/weekly-etf-eu
Workflow: Weekly ETF EU corrected report resend
Branch: main

delivery_mode: validate_only
correction_control_id: 20260713_180000
repair_run_id: 20260713_180000
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_180000.md
send_confirmation: not_confirmed
```

This run must:

```text
1. build the new sanitized correction package
2. copy only the 20260713_180000 approved preview files
3. recalculate all four file hashes
4. prove source and delivery byte identity
5. revalidate machine, visual and authority-separation gates
6. validate the correction queue
7. persist the new package and run manifest
8. perform no transport
```

Expected:

```text
corrected_resend_prepared=true
package_byte_identity_passed=true
transport_attempted=false
transport_success=false
corrected_resend_executed=false
receipt_confirmed=false
```

## After validate-only succeeds

Run the same workflow with:

```text
delivery_mode: dry_run
correction_control_id: 20260713_180000
repair_run_id: 20260713_180000
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_180000.md
send_confirmation: not_confirmed
```

Expected:

```text
attachment_count=4
transport_attempted=false
transport_success=false
send_executed=false
receipt_confirmed=false
original_transport_evidence_overwritten=false
```

Stop after verified dry-run success. Do not execute live send inside FIX2A.

## Delivery boundary

```text
send_or_resend_allowed=false
correction_transport_allowed=false
receipt_check_allowed=false
production_delivery_complete=false
```

After successful validate-only and dry-run, the next action becomes:

```text
EXPLICITLY_DISPATCH_SANITIZED_CORRECTED_RESEND
```

Do not reuse correction package `20260713_000000`. Do not create MVP31.
