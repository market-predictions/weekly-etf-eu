# Weekly ETF EU Review OS — Next Actions

Current priority: **DISPATCH_PREPARED_ROUTINE_WEEKLY_ETF_EU_RUN**.

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

## Prepared current run

```text
routine_run_id=20260712_125000
report_date=2026-07-12
report_suffix=260712
request_artifact=control/run_queue/etf_eu_routine_report_request_20260712_125000.md
workflow_file=.github/workflows/run-weekly-etf-eu-routine.yml
workflow_name=Weekly ETF EU routine production run
workflow_dispatch_available=true
workflow_dispatch_performed=false
fresh_package_generated=false
transport_attempted=false
receipt_confirmed=false
```

## Exact next action

In GitHub:

```text
Repository: market-predictions/weekly-etf-eu
Actions workflow: Weekly ETF EU routine production run
Branch: main
request_path: control/run_queue/etf_eu_routine_report_request_20260712_125000.md
```

Click **Run workflow** once. Do not create another request or change the run identity.

After the run, verify committed current-run pricing, Dutch/English Markdown–HTML–PDF files, readiness evidence, transport result and delivery evidence. Then perform the delayed independent receipt check and closeout.

## Standing upstream-first reuse rule

Use `market-predictions/weekly-etf` for mature architecture and evidence patterns only. Keep `weekly-etf-eu` and its current EU/UCITS state as authority.

## Architecture-package rule

This remains a routine production run. Do not create MVP31. Create a narrow repair only if this workflow produces a specific failed step or invalid artifact.
