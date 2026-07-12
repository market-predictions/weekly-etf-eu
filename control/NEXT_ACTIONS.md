# Weekly ETF EU Review OS — Next Actions

Current priority: **DISPATCH_REPAIRED_ROUTINE_WEEKLY_ETF_EU_RUN**.

## Latest completed cycle

```text
work_package_id=ETF-EU-MVP30_PRODUCTION_DELIVERY_CLOSEOUT_AND_ROUTINE_RUNBOOK
status=completed_production_delivery_closeout
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
runtime_run_id=20260711_175327
transport_success=true
send_executed=true
receipt_confirmed_from_new_run=true
production_delivery_cycle_closed=true
routine_production_ready=true
operating_mode=routine_production
```

## Active routine run

```text
routine_run_id=20260712_125000
report_date=2026-07-12
report_suffix=260712
request_artifact=control/run_queue/etf_eu_routine_report_request_20260712_125000.md
workflow_file=.github/workflows/run-weekly-etf-eu-routine.yml
workflow_name=Weekly ETF EU routine production run
workflow_dispatch_attempts=2
latest_attempt_status=failed_before_delivery
first_failure=builder_invoked_as_file_instead_of_module
second_failure=routine_manifest_missing_send_executed_false
first_failure_fixed=true
second_failure_fixed=true
fast_preflight_added=true
fresh_package_committed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
```

## Exact next action

Start a **new** workflow run from the current `main` branch:

```text
Repository: market-predictions/weekly-etf-eu
Actions workflow: Weekly ETF EU routine production run
Branch: main
request_path: control/run_queue/etf_eu_routine_report_request_20260712_125000.md
```

Do not use **Re-run failed jobs** on either previous attempt, because GitHub reruns the historical commit associated with that attempt. Do not create a second request or change the run identity.

The repaired workflow now performs a fast import and manifest-contract preflight before the slower UCITS pricing stage.

After the run, verify committed current-run pricing, Dutch/English Markdown–HTML–PDF files, readiness evidence, transport result and delivery evidence. Then perform the delayed independent receipt check and production closeout.

## Standing upstream-first reuse rule

Use `market-predictions/weekly-etf` for mature architecture and evidence patterns only. Keep `weekly-etf-eu` and its current EU/UCITS state as authority.

## Architecture-package rule

This remains a routine production run. Do not create MVP31. Create a narrow repair only for a specific failed step or invalid artifact.
