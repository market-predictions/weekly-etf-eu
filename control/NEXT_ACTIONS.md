# Weekly ETF EU Review OS — Next Actions

Current priority: **RERUN_CLIENT_SURFACE_REPAIR_PREVIEW_WITH_V2**.

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
latest_corrected_resend_workflow_run_id=29411450220
latest_corrected_resend_job_id=87339249817
latest_corrected_resend_attempt_status=blocked_before_package_preparation
latest_corrected_resend_failure=visual_review_did_not_pass
visual_review_completed=true
visual_layout_gate_passed=true
client_surface_language_clean=false
pdf_visual_gate_passed=false
client_surface_sanitizer_v2_created=true
client_surface_preview_workflow_v2_enabled=true
semantic_pricing_header_gate_created=true
new_corrected_package_prepared=false
new_dry_run_completed=false
correction_transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
```

## Why the corrected-resend run failed

The corrected-resend workflow behaved correctly. Package creation requires `visual_review_passed=true`, while the committed review artifact remained false. The workflow therefore stopped before validate-only, dry-run, authorization or send.

Manual inspection found that layout and pagination passed, but the Dutch client text still contained:

```text
Trading line / Markt as pricing-table headers
broker- en bevestiging van de handelslijn
afzonderlijke afzonderlijk besluit
```

The visual gate was not promoted. Sanitizer v2 and the semantic PDF language gate now reject these defects automatically.

## Exact next action

Start a fresh preview workflow from current `main`:

```text
Repository: market-predictions/weekly-etf-eu
Workflow: Weekly ETF EU client-surface repair preview
Branch: main
source_run_id: 20260712_125000
sanitization_run_id: 20260713_180000
report_suffix: 260712
```

Do not use **Re-run failed jobs** on corrected-resend run `29411450220`.
Do not run corrected-resend validate-only until the new preview has completed and its visual gate is explicitly approved.

## Expected v2 preview behavior

```text
1. apply deterministic client-language sanitizer v2
2. use Handelslijn and Peildatum in the Dutch pricing table
3. use Trading line and Pricing date in the English pricing table
4. remove the malformed Dutch phrases found during manual review
5. rerender Dutch and English HTML/PDF
6. enforce the semantic pricing-header and client-language machine gate
7. rerender first, middle and last pages
8. persist a new visual-review-pending artifact
9. perform no transport
```

## Review after the v2 preview

Inspect:

```text
output/repair_preview/20260713_180000/pages/nl/first_001.png
output/repair_preview/20260713_180000/pages/nl/middle_002.png
output/repair_preview/20260713_180000/pages/nl/last_003.png
output/repair_preview/20260713_180000/pages/en/first_001.png
output/repair_preview/20260713_180000/pages/en/middle_002.png
output/repair_preview/20260713_180000/pages/en/last_003.png
```

Require:

```text
no right-edge or bottom clipping
no overlap
readable tables and headings
correct Dutch Unicode
sections 1-7 present
section 8 absent
no raw status or authority metadata
semantic pricing-date headers correct
client language natural and grammatically correct
no duplicate title
```

Only then may:

```text
visual_review_passed=true
client_surface_language_clean=true
blockers=[]
```

be recorded.

## After passed v2 visual review

Run corrected resend in validate-only mode:

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

After a passed v2 visual review and successful new dry run, the next action becomes:

```text
EXPLICITLY_DISPATCH_SANITIZED_CORRECTED_RESEND
```

Do not reuse correction package `20260713_000000`. Do not create MVP31.
