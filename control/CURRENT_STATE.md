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
source_work_package=ETF-EU-MVP29_DELIVERY_RUN_MONITOR_AND_RECEIPT_EVIDENCE
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
run_id=20260710_000000
runtime_run_id=20260711_175327
report_date=2026-07-10
report_suffix=260710
transport_success=true
send_executed=true
receipt_confirmed_from_new_run=true
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
production_delivery_closeout_manifest=output/run_manifests/etf_eu_production_delivery_closeout_manifest_20260711_175327.json
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
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
workflow_dispatch_attempts=2
latest_attempt_status=failed_before_delivery
latest_failure_stage=Validate routine package readiness
latest_failure_reason=routine_manifest_missing_explicit_send_executed_false
first_failure_fixed=python_module_invocation_corrected
second_failure_fixed=routine_manifest_send_executed_field_added
fast_preflight_added=true
repair_commit_manifest_contract=c6d97e605caafba6a353c54b30ec53ef5b1ed9aa
repair_commit_preflight=66a73728a03d2b1b4347cb6cbaf1061dc61fb613
fresh_package_committed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
status=repaired_awaiting_new_workflow_dispatch
selected_next_action=DISPATCH_REPAIRED_ROUTINE_WEEKLY_ETF_EU_RUN
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

## Current note

The active routine run has not sent anything. Two workflow attempts failed before delivery: first on Python package invocation, then because the new routine manifest omitted an explicit `send_executed=false` field required by the readiness gate. Both defects are repaired on `main`, and a fast preflight now checks imports and the initial manifest contract before the slower pricing stage. Start a new workflow run from current `main`; do not rerun an old failed attempt and do not create a new run identity.
