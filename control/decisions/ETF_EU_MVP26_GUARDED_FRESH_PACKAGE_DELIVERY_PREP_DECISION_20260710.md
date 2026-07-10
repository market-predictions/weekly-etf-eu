# Decision — ETF-EU-MVP26 Guarded Fresh Package Delivery Prep

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_DECISION_20260710`

## Decision

Close MVP26 as guarded delivery preparation for the MVP25 readiness-gated fresh Weekly ETF EU package.

```text
status=completed_guarded_fresh_package_delivery_prep
upstream_pattern_adapted=weekly-etf guarded delivery and delivery-manifest concept; adapted for EU explicit delivery-prep without send authority
ready_for_controlled_delivery=true
delivery_authorized=false
send_executed=false
transport_attempted=false
selected_next_package=ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION
```

## Upstream basis

MVP26 inspected the closest upstream `weekly-etf` guarded-delivery and delivery-manifest patterns:

```text
send_report_runtime_html.py
send_report.py
tools/write_etf_delivery_manifest_summary.py
tools/write_weekly_etf_run_manifest.py
tools/validate_etf_manifest_evidence.py
```

The adapted upstream concepts are:

```text
pre-send guard separation
HTML/PDF/report package evidence discipline
redacted delivery manifest design
run-manifest pointer and artifact handoff
no delivery success claim without delivery evidence
```

## EU adaptation

The EU delivery-prep layer validates explicit EU package artifacts rather than using the legacy U.S. `weekly_analysis*` sender discovery path.

Reason:

```text
U.S. report filenames, U.S. portfolio state, U.S. holdings, recipient authority and delivery assumptions are not EU authority.
```

## Delivery-prep result

MVP26 creates:

```text
control/ETF_EU_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_CONTRACT_V1.md
tools/prepare_etf_eu_guarded_fresh_package_delivery.py
tools/validate_etf_eu_guarded_fresh_package_delivery_prep.py
output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260710_000000.json
tests/test_etf_eu_guarded_fresh_package_delivery_prep.py
```

and updates:

```text
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

## Authority rules

`ready_for_controlled_delivery=true` remains package eligibility only. It is not send authority.

MVP26 must not create:

```text
delivery_authorized=true
send_command_allowed=true
workflow_dispatch_allowed=true
run_queue_allowed=true
send_executed=true
transport_attempted=true
receipt_confirmed=true
valuation_grade=true
funding_authority=true
portfolio_mutation=true
production_delivery_authority=true
```

Those fields remain false.

No recipients, SMTP secrets, plaintext recipient values, or raw receipt PDFs are exposed.

## Consequence

The package is prepared for a later explicit guarded-send authorization package. The next package should be:

```text
ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION
```

MVP27 may ask for explicit user authorization and guarded-send confirmation. MVP26 does not send, dispatch, queue, transport, or confirm receipt.
