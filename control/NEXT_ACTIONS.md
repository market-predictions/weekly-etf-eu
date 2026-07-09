# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP20**.

## Latest completion

```text
work_package_id=ETF-EU-MVP19-FIX2
status=completed_client_grade_package_ready_for_controlled_resend
source_work_package=ETF-EU-MVP19-FIX
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
actual_close_fetch_completed=true
ucits_close_price_validation_line_count=11
ucits_close_price_validation_priced_line_count=10
ucits_close_price_validation_failed_line_count=1
ucits_close_price_validation_venue_count=3
ucits_close_price_validation_currency_count=3
client_grade_package_ready=true
pdf_output_available=true
html_output_available=true
resend_performed=false
delivery_success_closed=false
receipt_confirmed=false
completion_claimed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=client_grade_package_ready_for_controlled_resend
selected_next_package=ETF-EU-MVP20
```

## Active next package

```text
ETF-EU-MVP20
```

## ETF-EU-MVP20 objective

Prepare or execute the guarded controlled resend step for the existing `ETF-EU-MVP19-FIX2` client-grade package.

Do **not** execute transport unless the user explicitly instructs it.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/work_packages/ETF_EU_MVP20_GUARDED_CONTROLLED_RESEND_INSTRUCTIONS_20260709.md
```

Then inspect only the minimum relevant transport files:

```text
.github/workflows/send-weekly-etf-eu-report.yml
send_report.py
output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json
```

## Required validation before any transport decision

```bash
python tools/validate_ucits_close_price_validation_basket_results.py \
  --artifact output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json

python tools/validate_etf_eu_delivery_package_manifest.py \
  --manifest output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json

python tools/validate_etf_eu_mvp19_fix2_ready_for_controlled_resend.py \
  --artifact output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json
```

## Transport authority rule

A resend may only be marked successful if the delivery layer emits a real receipt, manifest, or equivalent evidence.

If the current EU workflow still contains a transport placeholder, report:

```text
status=blocked_transport_placeholder_no_delivery_performed
```

and do not claim delivery.

## Guardrail

No queue file, workflow dispatch, email sending, transport command, or delayed receipt check should be started from this state update alone.
