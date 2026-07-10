# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION**.

## Latest completion

```text
work_package_id=ETF-EU-MVP20A_REAL_TRANSPORT_LAYER_IMPLEMENTATION
status=completed_real_transport_layer_implemented_not_executed
source_work_package=ETF-EU-MVP20
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
real_eu_transport_runner_created=true
real_eu_transport_runner=runtime/send_etf_eu_delivery_package.py
workflow_placeholder_transport_removed=true
workflow_uses_real_eu_transport_runner=true
push_trigger_forces_validate_only=true
guarded_send_requires_delivery_mode_send=true
guarded_send_requires_confirm_guarded_send=true
delivery_evidence_contract_extended=true
receipt_check_confirms_false_without_real_receipt=true
existing_client_grade_package_input=ETF-EU-MVP19-FIX2
client_grade_package_ready=true
ready_for_controlled_resend=true
resend_performed=false
send_executed=false
delivery_success_closed=false
receipt_confirmed=false
completion_claimed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=real_transport_layer_implemented_not_executed
selected_next_package=ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION
```

## Active next package

```text
ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION
```

## Standing upstream-first reuse rule

Before creating or materially changing any ETF EU task, work package, workflow, runtime script, validator, renderer, delivery step, or control file, first inspect the closest upstream `market-predictions/weekly-etf` implementation.

Record one of:

```text
upstream_pattern_reused=<file or concept>
upstream_pattern_adapted=<file or concept + reason>
upstream_pattern_rejected=<file or concept + EU authority reason>
no_upstream_equivalent_found=<search terms / inspected files>
```

Borrow mature concepts and safeguards. Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## ETF-EU-MVP20B objective

Execute the guarded controlled resend of the existing `ETF-EU-MVP19-FIX2` client-grade package through the real EU package transport runner.

Do **not** execute transport unless the user explicitly instructs it.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/work_packages/ETF_EU_MVP20_GUARDED_CONTROLLED_RESEND_INSTRUCTIONS_20260709.md
control/decisions/ETF_EU_MVP20A_REAL_TRANSPORT_LAYER_DECISION_20260710.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
```

Then inspect only the minimum relevant EU execution files:

```text
.github/workflows/send-weekly-etf-eu-report.yml
runtime/send_etf_eu_delivery_package.py
runtime/check_etf_eu_delivery_receipt.py
tools/validate_etf_eu_delivery_evidence.py
output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json
```

And inspect the closest upstream `weekly-etf` delivery pattern before modifying anything:

```text
market-predictions/weekly-etf:.github/workflows/send-weekly-report.yml
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
market-predictions/weekly-etf:send_report_OLD.py
market-predictions/weekly-etf:tools/write_etf_delivery_manifest_summary.py
market-predictions/weekly-etf:tools/write_weekly_etf_run_manifest.py
```

## Required validation before execution

```bash
python tools/validate_ucits_close_price_validation_basket_results.py \
  --artifact output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json

python tools/validate_etf_eu_delivery_package_manifest.py \
  --manifest output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json

python tools/validate_etf_eu_mvp19_fix2_ready_for_controlled_resend.py \
  --artifact output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json

pytest tests/test_etf_eu_mvp19_fix2_ready_for_controlled_resend.py
pytest tests/test_etf_eu_delivery_evidence.py
pytest tests/test_etf_eu_real_transport_layer.py
```

## Execution path when explicitly instructed

Use workflow dispatch only:

```text
delivery_mode=send
send_confirmation=confirm_guarded_send
```

Push-triggered runs are forced to `validate_only` and cannot send.

## Transport authority rule

A resend may only be marked successful if the delivery layer emits real evidence with:

```text
transport_attempted=true
transport_success=true
message_id_or_receipt_reference populated
receipt_confirmed=false unless separately verified
```

A SMTP success means transport returned without exception; it is not an end-recipient inbox receipt.

## Guardrail

No queue file, workflow dispatch, email sending, transport command, or delayed receipt check should be started from this state update alone.
