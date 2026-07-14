# Weekly ETF EU Review OS — Next Actions

Current priority: **RUN_CLIENT_SURFACE_REPAIR_PREVIEW**.

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
client_surface_cleanup_required=true
live_corrected_resend_allowed=false
sanitized_preview_generated=false
client_surface_clean=false
authority_separation_gate_passed=false
pdf_machine_gate_passed=false
pdf_visual_gate_passed=false
new_corrected_package_prepared=false
new_dry_run_completed=false
correction_transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
```

## Exact next action — client-surface repair preview

Start a new GitHub Actions workflow run from current `main`:

```text
Repository: market-predictions/weekly-etf-eu
Workflow: Weekly ETF EU client-surface repair preview
Branch: main
source_run_id: 20260712_125000
sanitization_run_id: 20260713_180000
report_suffix: 260712
```

This workflow must:

```text
1. remove the client Authority flags section
2. replace raw status enums with Dutch and English client labels
3. preserve prices, ISINs, tickers, report date and recommendation
4. render sanitized Dutch and English HTML/PDF
5. validate forbidden-token absence
6. validate sections 1-7 and semantic tables
7. validate authority evidence separation
8. render first, middle and last pages
9. persist a visual-review-pending artifact
10. perform no transport
```

## Required manual review after the preview succeeds

Inspect the first, middle and last page renders for both languages and confirm:

```text
no clipping
no overlapping text
readable tables and headings
correct Dutch Unicode
sections 1-7 visible
section 8 absent
raw verification enums absent
authority and transport flags absent
client wording natural and professional
```

Only after actual inspection may the visual-review artifact be updated to:

```text
visual_review_passed=true
blockers=[]
```

## After visual approval

Run the generalized corrected-report workflow in validate-only mode:

```text
Workflow: Weekly ETF EU corrected report resend
delivery_mode: validate_only
correction_control_id: 20260713_180000
repair_run_id: 20260713_180000
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_180000.md
send_confirmation: not_confirmed
```

Then run the same workflow in dry-run mode:

```text
delivery_mode: dry_run
correction_control_id: 20260713_180000
repair_run_id: 20260713_180000
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_180000.md
send_confirmation: not_confirmed
```

Stop after verified dry-run success. Do not select live send during FIX2A.

## Superseded package boundary

The following historical package and dry-run evidence remain preserved but may not be used for live transport:

```text
output/delivery_control/etf_eu_corrected_resend_package_20260713_000000.json
output/delivery/etf_eu_corrected_transport_result_20260713_165614.json
output/delivery/etf_eu_corrected_delivery_evidence_20260713_165614.json
output/corrected_delivery_package/20260713_000000/
```

The package validator must reject correction control id `20260713_000000` because its supersession artifact contains `superseded=true` and `live_send_allowed=false`.

## Delivery boundary

```text
send_or_resend_allowed=false
correction_transport_allowed=false
receipt_check_allowed=false
production_delivery_complete=false
```

The next action after completed FIX2A is:

```text
EXPLICITLY_DISPATCH_SANITIZED_CORRECTED_RESEND
```

only after the sanitized preview, visual review, new package hashes and new dry run have all passed. Do not create MVP31.
