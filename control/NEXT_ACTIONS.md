# Weekly ETF EU Review OS — Next Actions

Current priority: **RUN_CORRECTED_RESEND_VALIDATE_ONLY**.

## Active package

```text
work_package_id=ETF-EU-RUN260712-FIX2_EXPLICIT_CORRECTED_REPORT_RESEND
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
repair_run_id=20260712_200000
correction_control_id=20260713_000000
report_date=2026-07-12
report_suffix=260712
corrected_client_output_valid=true
implementation_ready=true
package_materialization_pending=true
corrected_resend_prepared=false
corrected_resend_executed=false
correction_transport_attempted=false
correction_transport_success=false
receipt_confirmed=false
```

## Exact next action — validate only

Start this workflow from current `main`:

```text
Repository: market-predictions/weekly-etf-eu
Workflow: Weekly ETF EU corrected report resend
Branch: main
delivery_mode: validate_only
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_000000.md
send_confirmation: not_confirmed
```

This run must:

```text
1. copy the four approved repair-preview files into the correction package
2. use corrected Dutch and English filenames
3. verify source and delivery SHA-256 identity
4. revalidate machine and visual gates
5. validate the correction queue
6. persist the package, preparation artifact and correction run manifest
7. perform no transport
```

## After validate-only succeeds

Run the same workflow in dry-run mode:

```text
delivery_mode: dry_run
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_000000.md
send_confirmation: not_confirmed
```

Expected dry-run state:

```text
transport_attempted=false
transport_success=false
corrected_resend_executed=false
receipt_confirmed=false
```

## Live correction boundary

Do not select live execution until validate-only and dry-run have succeeded and been verified.

The workflow supports a separately guarded live branch. The required confirmation value is recorded in the correction contract and workflow; it is not implied by package implementation or by validate-only/dry-run success.

## Approved source files

```text
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.pdf
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.pdf
```

## Forbidden correction attachments

```text
output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf
output/fresh_generation/weekly_etf_eu_review_260712.pdf
```

## Delivery and privacy boundary

```text
original_transport_evidence_overwritten=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
raw_receipt_pdf_stored_in_github=false
receipt_confirmed=false
production_delivery_complete=false
```

After successful corrected transport, the next action is delayed independent receipt verification. Do not create MVP31; keep this as a narrow run-specific correction package.
