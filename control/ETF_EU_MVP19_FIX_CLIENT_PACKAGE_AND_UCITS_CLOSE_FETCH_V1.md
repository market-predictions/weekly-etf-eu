# ETF-EU-MVP19-FIX client package and UCITS close-fetch v1

## Purpose

Implement the infrastructure needed to make the EU delivery package client-grade before a later controlled resend.

## Authority rule

```text
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
resend_performed=false
delivery_success_closed=false
receipt_confirmed=false
completion_claimed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

## Implemented in this package

```text
close_fetch_runner_created=true
client_surface_renderer_cleaned=true
pdf_package_renderer_created=true
pdf_package_manifest_validator_created=true
sender_requires_pdf_package_support=true
workflow_requires_pdf_package_support=true
```

## Not completed in this package

```text
live_close_fetch_artifact_created=false
package_manifest_created=false
controlled_resend_performed=false
```

## Decision

```text
readiness_status=client_package_or_price_fetch_hardening_still_required
selected_next_package=ETF-EU-MVP19-FIX2
```
