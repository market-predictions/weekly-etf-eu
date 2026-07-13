# Weekly ETF EU Review OS — Next Actions

Current priority: **EXPLICITLY_DISPATCH_CORRECTED_RESEND**.

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
package_materialization_pending=false
package_byte_identity_passed=true
corrected_resend_prepared=true
dry_run_workflow_run_id=29268423307
dry_run_runtime_run_id=20260713_165614
dry_run_completed=true
corrected_resend_executed=false
correction_transport_attempted=false
correction_transport_success=false
receipt_confirmed=false
```

## Verified dry-run result

```text
delivery_mode=dry_run
delivery_status=dry_run_no_transport
attachment_count=4
transport_attempted=false
transport_success=false
send_executed=false
receipt_confirmed=false
original_transport_evidence_overwritten=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
```

## Exact next action — explicit guarded resend

Start a new workflow run from current `main`:

```text
Repository: market-predictions/weekly-etf-eu
Workflow: Weekly ETF EU corrected report resend
Branch: main
delivery_mode: send
queue_path: control/run_queue/etf_eu_corrected_resend_request_20260713_000000.md
send_confirmation: confirm_corrected_resend
```

This is the only authorized live correction path. Do not use the normal routine-generation workflow and do not reuse the malformed original PDFs.

## Expected corrected-send state

```text
corrected_resend_executed=true
correction_transport_attempted=true
correction_transport_success=true
delivery_status=smtp_sendmail_returned_no_exception
receipt_confirmed=false
original_transport_evidence_overwritten=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
```

Expected correction evidence:

```text
output/delivery_authorization/etf_eu_corrected_resend_authorization_<runtime_run_id>.json
output/delivery/etf_eu_corrected_transport_result_<runtime_run_id>.json
output/delivery/etf_eu_corrected_delivery_evidence_<runtime_run_id>.json
```

## Approved correction attachments

```text
output/corrected_delivery_package/20260713_000000/weekly_etf_eu_review_nl_260712_gecorrigeerd.pdf
output/corrected_delivery_package/20260713_000000/weekly_etf_eu_review_260712_corrected.pdf
output/corrected_delivery_package/20260713_000000/weekly_etf_eu_review_nl_260712_gecorrigeerd.html
output/corrected_delivery_package/20260713_000000/weekly_etf_eu_review_260712_corrected.html
```

## Forbidden correction attachments

```text
output/fresh_generation/weekly_etf_eu_review_nl_260712.pdf
output/fresh_generation/weekly_etf_eu_review_260712.pdf
```

## After successful corrected transport

Wait approximately ten minutes and perform independent mailbox receipt verification. Confirm the corrected Dutch PDF, English PDF, Dutch HTML and English HTML using hashes and attachment flags only. Keep `receipt_confirmed=false` until that evidence exists.

Do not perform an automatic second resend. Do not create MVP31. After confirmed corrected receipt, close the correction chain and return to normal routine-production mode.
