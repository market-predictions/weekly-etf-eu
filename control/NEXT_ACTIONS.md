# Weekly ETF EU Review OS — Next Actions

Current priority: **COMPLETE_SANITIZED_PDF_VISUAL_REVIEW**.

## Active package

```text
work_package_id=ETF-EU-RUN260712-FIX2A_CLIENT_SURFACE_SANITIZATION_BEFORE_RESEND
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
previous_repair_run_id=20260712_200000
previous_correction_control_id=20260713_000000
sanitization_run_id=20260713_180000
new_correction_control_id=20260713_180000
report_date=2026-07-12
report_suffix=260712
previous_corrected_package_superseded=true
previous_corrected_package_live_send_allowed=false
live_corrected_resend_allowed=false
sanitized_preview_generated=true
sanitized_preview_commit=f0d07ac7ec2ede1825cc868f162b45d7060ad7b6
client_surface_sanitization_passed=true
client_surface_clean=true
authority_separation_gate_passed=true
pdf_machine_gate_passed=true
pdf_visual_gate_passed=false
visual_review_pending=true
dutch_pdf_page_count=3
english_pdf_page_count=3
new_corrected_package_prepared=false
new_dry_run_completed=false
correction_transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
```

## Verified machine and separation results

```text
Dutch client-surface clean=true
English client-surface clean=true
forbidden tokens=[]
raw status enums absent=true
authority metadata absent=true
authority flags preserved in internal evidence=true
sections 1-7 present=true
section 7 near end=true
semantic tables=true
pricing lines represented=11
Dutch PDF pages=3
English PDF pages=3
machine blockers=[]
```

## Exact next action — explicit visual review

Inspect these committed page renders:

```text
output/repair_preview/20260713_180000/pages/nl/first_001.png
output/repair_preview/20260713_180000/pages/nl/middle_002.png
output/repair_preview/20260713_180000/pages/nl/last_003.png
output/repair_preview/20260713_180000/pages/en/first_001.png
output/repair_preview/20260713_180000/pages/en/middle_002.png
output/repair_preview/20260713_180000/pages/en/last_003.png
```

Confirm:

```text
no right-edge clipping
no bottom clipping
no overlapping text
tables and headings readable
Dutch Unicode correct
sections 1-7 visible
section 8 absent
raw verification enums absent
authority and transport flags absent
client wording natural and professional
duplicate title absent
```

Only after actual inspection may this artifact be promoted:

```text
output/quality/etf_eu_routine_pdf_visual_review_20260713_180000.json
```

Required passed state:

```text
visual_review_passed=true
blockers=[]
client_surface_language_clean=true
```

## After visual approval

Run the generalized corrected-report workflow in validate-only mode:

```text
Workflow: Weekly ETF EU corrected report resend
Branch: main
delivery_mode: validate_only
correction_control_id: 20260713_180000
repair_run_id: 20260713_180000
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_180000.md
send_confirmation: not_confirmed
```

Then run dry-run with the same identity and:

```text
delivery_mode: dry_run
send_confirmation: not_confirmed
```

Stop after verified dry-run success. Do not execute live send inside FIX2A.

## Delivery boundary

```text
send_or_resend_allowed=false
correction_transport_allowed=false
receipt_check_allowed=false
production_delivery_complete=false
```

The next action after passed visual review and a successful new dry run is:

```text
EXPLICITLY_DISPATCH_SANITIZED_CORRECTED_RESEND
```

Do not reuse the superseded `20260713_000000` package. Do not create MVP31.
