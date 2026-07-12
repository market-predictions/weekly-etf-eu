# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-12

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Latest completed package

```text
work_package_id=ETF-EU-MVP30_PRODUCTION_DELIVERY_CLOSEOUT_AND_ROUTINE_RUNBOOK
status=completed_production_delivery_closeout
source_work_package=ETF-EU-MVP29_DELIVERY_RUN_MONITOR_AND_RECEIPT_EVIDENCE
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf delivery manifest, final run-manifest and routine closeout concepts adapted for EU current-package authority, independent receipt evidence and hashes-only mailbox metadata
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
run_id=20260710_000000
runtime_run_id=20260711_175327
report_date=2026-07-10
report_suffix=260710
transport_result_artifact=output/delivery/etf_eu_current_package_transport_result_20260711_175327.json
delivery_evidence_artifact=output/delivery/etf_eu_current_package_delivery_evidence_20260711_175327.json
receipt_evidence_artifact=output/delivery/etf_eu_current_package_receipt_evidence_20260711_175327.json
receipt_monitor_artifact=output/delivery_control/etf_eu_delivery_run_monitor_receipt_20260710_000000.json
production_delivery_closeout_manifest=output/run_manifests/etf_eu_production_delivery_closeout_manifest_20260711_175327.json
routine_production_runbook=control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
transport_attempted=true
transport_success=true
send_executed=true
receipt_check_status=receipt_confirmed
receipt_confirmed_from_new_run=true
expected_attachment_set_seen=true
attachment_count_seen=4
production_delivery_cycle_closed=true
routine_production_ready=true
operating_mode=routine_production
architecture_enablement_cycle_closed=true
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
raw_receipt_pdf_stored_in_github=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
selected_next_action=DISPATCH_PREPARED_ROUTINE_WEEKLY_ETF_EU_RUN
```

## Active operating mode

```text
ROUTINE_WEEKLY_ETF_EU_PRODUCTION
```

## Active routine run

```text
routine_run_id=20260712_125000
report_date=2026-07-12
report_suffix=260712
request_artifact=control/run_queue/etf_eu_routine_report_request_20260712_125000.md
workflow_file=.github/workflows/run-weekly-etf-eu-routine.yml
workflow_dispatch_available=true
workflow_dispatch_performed=false
fresh_package_generated=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
status=prepared_awaiting_manual_workflow_dispatch
selected_next_action=DISPATCH_PREPARED_ROUTINE_WEEKLY_ETF_EU_RUN
```

## Routine production authority

```text
canonical_runbook=control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
new_run_id_required=true
new_report_date_required=true
new_report_suffix_required=true
prior_run_artifacts_are_historical_only=true
weekly_etf_eu_source_of_truth=true
weekly_etf_upstream_donor_only=true
```

## Production closeout note

The first current-package production cycle remains closed and verified. The next fresh routine run is fully prepared but has not executed because connector-authored commits did not start the GitHub Actions workflow. Dispatch the prepared routine workflow manually; do not create a second run identity or reuse previous dated artifacts.
