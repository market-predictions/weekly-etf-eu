# Weekly ETF EU Review OS — Next Actions

Current priority: **RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT**.

## Latest completion

```text
work_package_id=ETF-EU-MVP30_PRODUCTION_DELIVERY_CLOSEOUT_AND_ROUTINE_RUNBOOK
status=completed_production_delivery_closeout
source_work_package=ETF-EU-MVP29_DELIVERY_RUN_MONITOR_AND_RECEIPT_EVIDENCE
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
runtime_run_id=20260711_175327
transport_success=true
send_executed=true
receipt_confirmed_from_new_run=true
expected_attachment_set_seen=true
production_delivery_closeout_manifest=output/run_manifests/etf_eu_production_delivery_closeout_manifest_20260711_175327.json
routine_production_runbook=control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
production_delivery_cycle_closed=true
routine_production_ready=true
operating_mode=routine_production
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
raw_receipt_pdf_stored_in_github=false
next_action=RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT
```

## Standing upstream-first reuse rule

Before changing ETF EU workflow, runtime, validation, pricing, state, rendering or control files, inspect the closest upstream `market-predictions/weekly-etf` implementation and record the reuse/adaptation decision.

Do not port U.S. portfolio state, holdings, instruments or authority assumptions as EU authority.

## Active operating mode

```text
ROUTINE_WEEKLY_ETF_EU_PRODUCTION
```

## Next routine action

Follow:

```text
control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
```

The next report must use a new report date, report suffix, run id and complete current-run artifact set.

Do not reuse the `20260710` or `20260711` artifacts as current-run authority. They are historical proof of the first completed production cycle.

## Architecture-package rule

Do not create an MVP31 package by default. Create a narrow package only for a specific defect, failed validator, broken contract, missing evidence path or material capability change. Otherwise, execute the next report as a routine operation.
