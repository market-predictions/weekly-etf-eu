# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-07-17
repository=market-predictions/weekly-etf-eu
operating_mode=routine_production_with_three_position_active_model_portfolio
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
selected_next_action=MANUAL_DISPATCH_ACCEPTED_PACKAGE_20260717_141500
```

## Latest completed delivery

```text
report_date=2026-07-12
github_workflow_run_id=29428021408
receipt_confirmed=true
production_delivery_cycle_closed=true
```

This remains the latest independently confirmed email-delivery cycle. The 2026-07-17 package has not yet performed transport.

## Active broker-neutral model portfolio

```text
starting_capital_eur=100000.00
nav_eur=100016.60
cash_eur=60439.44
invested_market_value_eur=39577.16
cash_weight_pct=60.4294
position_count=3
model_portfolio_only=true
real_broker_execution=false
```

| Position | ISIN | Shares | Model price | Market value | Weight | Current status |
|---|---|---:|---:|---:|---:|---|
| VWCE | IE00BK5BQT80 | 151 | €165.32 | €24,963.32 | 24.959177% | Funded global-core first tranche |
| EUNA | IE00BDBRDM35 | 1,526 | €4.913 | €7,497.24 | 7.495996% | Funded aggregate-bond first tranche |
| SXR8 | IE00B5BMR087 | 10 | €711.66 | €7,116.60 | 7.115419% | Hold; no second tranche authorised |

Cash plus invested market value reconciles exactly to NAV at eurocent precision.

## Accepted report package

```text
run_id=20260717_141500
report_date=2026-07-17
report_suffix=260717_06
source_workflow_run_id=29575699421
machine_validation_passed=true
visual_review_passed=true
dutch_page_count=6
english_page_count=6
client_grade_preview_accepted=true
readiness_gate_passed=true
ready_for_controlled_delivery=true
```

Authoritative evidence:

```text
output/quality/etf_eu_client_grade_v2_validation_20260717_141500.json
output/quality/etf_eu_routine_pdf_client_grade_20260717_141500.json
output/quality/etf_eu_routine_pdf_visual_review_20260717_141500.json
output/quality/etf_eu_routine_package_readiness_20260717_141500.json
output/run_manifests/etf_eu_routine_preview_manifest_20260717_141500.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-17_20260717_141500.json
```

The accepted package contains Dutch-primary and English-companion HTML/PDF output. All twelve rendered pages were reviewed at high resolution. The final report has no known clipping, overlap, broken identifiers, orphaned headings or language mismatch.

## Immutable delivery lock

```text
lock_artifact=output/delivery_control/etf_eu_accepted_package_lock_20260717_141500.json
locked_file_count=4
lock_method=git_blob_sha_exact_byte_identity
```

Locked client files:

```text
output/fresh_generation/weekly_etf_eu_review_nl_260717_06.html
output/fresh_generation/weekly_etf_eu_review_nl_260717_06.pdf
output/fresh_generation/weekly_etf_eu_review_260717_06.html
output/fresh_generation/weekly_etf_eu_review_260717_06.pdf
```

The delivery validator recalculates each Git blob identity before transport. Any byte change blocks delivery.

## Guarded delivery preparation

```text
delivery_prep=output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260717_141500.json
authorization=output/delivery_authorization/etf_eu_guarded_send_authorization_20260717_141500.json
decision=output/delivery_control/etf_eu_controlled_delivery_decision_20260717_141500.json
transport_selection=output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260717_141500.json
prepared_queue=control/prepared_delivery/etf_eu_current_package_delivery_request_20260717_141500.md
delivery_authorized=true
send_command_allowed=true
send_confirmation_received=true
transport_attempted=false
send_executed=false
receipt_confirmed=false
```

The connector security boundary blocks creation of an automatically triggering live-send queue. One manual GitHub `workflow_dispatch` is therefore required. This is the only remaining external action before transport verification.

## Workflow to dispatch

```text
workflow=Weekly ETF EU current-package delivery workflow
branch=main
delivery_mode=send
queue_path=control/prepared_delivery/etf_eu_current_package_delivery_request_20260717_141500.md
send_confirmation=confirm_guarded_send
```

The workflow:

1. validates the package, authorization chain and exact-byte lock;
2. blocks duplicate successful delivery for this queue and suffix;
3. uses the existing current-package transport runner;
4. persists redacted result and evidence;
5. updates the routine manifest to awaiting-receipt state;
6. does not change portfolio state or regenerate the report.

## Authority boundaries

```text
canonical_identity=isin_plus_exact_share_class_plus_venue_plus_exchange_line_plus_currency
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
model_portfolio_only=true
real_broker_execution=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
transport_attempted=false
send_executed=false
receipt_confirmed=false
```

## Next closeout sequence

```text
manual guarded workflow dispatch
→ inspect workflow result and committed transport evidence
→ wait approximately ten minutes
→ independently verify receipt in connected mailbox
→ confirm four attachments and matching report identity
→ update routine manifest and production closeout
→ update CURRENT_STATE, NEXT_ACTIONS and DECISION_LOG
```

Do not claim completed delivery until independent receipt evidence sets `receipt_confirmed=true`.
