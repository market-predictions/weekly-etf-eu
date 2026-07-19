# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-07-19
repository=market-predictions/weekly-etf-eu
operating_mode=routine_production_with_three_position_active_model_portfolio
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
selected_next_action=RUN_WP33_EXACT_CURRENT_NON_DELIVERY_REPLAY
```

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

## Latest accepted and transported report

```text
report_run_id=20260717_141500
runtime_transport_run_id=20260717_170931
report_date=2026-07-17
report_suffix=260717_06
source_preview_workflow_run_id=29575699421
transport_workflow_run_id=29598942372
machine_validation_passed=true
visual_review_passed=true
readiness_gate_passed=true
transport_attempted=true
transport_success=true
send_executed=true
attachment_count=4
```

Authoritative transport evidence:

```text
output/delivery/etf_eu_current_package_transport_result_20260717_170931.json
output/delivery/etf_eu_current_package_delivery_evidence_20260717_170931.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-17_20260717_141500.json
```

An independent connected-mailbox check found the matching report with all four expected file roles. Connector privacy controls prevented persistence of mailbox-derived receipt metadata to GitHub. Therefore:

```text
independent_mailbox_match_observed=true
formal_receipt_artifact_persisted=false
production_delivery_cycle_closed_in_repo=false
resend_allowed=false
```

The report must not be resent. WP31 remains a governance closeout item only, pending an allowed privacy-minimal persistence route.

## WP32 additive cockpit preview

```text
work_package=ETF-EU-WP32_ADDITIVE_COCKPIT_FRONT_PAGE_PREVIEW
pull_request=61
merge_commit=348c324d911b142f0871e9a67f875b76b3450447
final_validation_run=29667194382
status=merged_validated_preview_only
production_enablement=false
```

Delivered capability:

```text
EU/UCITS cockpit front page
→ existing investor report
→ existing analyst report
```

Validation facts:

```text
NL_page_count=7
EN_page_count=7
classic_page_count=6
page_delta=1
classic_sections_preserved=15
regression_tests_passed=true
machine_validation_passed=true
primary_visual_review_passed=true
secondary_adversarial_review_passed=true
protected_inputs_unchanged=true
blockers=0
```

The implementation uses current normalized EU state, ISIN-first identity, EUR portfolio metrics, a separate email-safe inline renderer and a fail-closed feature gate:

```text
MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE=disabled|enabled
```

The feature remains preview-only. The routine package builder and production generation path have not yet been enabled.

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
cockpit_production_enablement=false
```

## Current development sequence

```text
WP32 merged and validated
→ WP33 exact-current non-delivery production replay
→ prove disabled rollback and enabled +1 page behavior
→ integrate only the output layer when all gates pass
→ record a separate production-enablement decision
→ keep actual future report delivery separately governed
```

Do not regenerate or resend the accepted 2026-07-17 package as part of WP33.