# ETF-EU-WP15Y closing-price POC decision

## Date

2026-07-03

## Decision

ETF-EU-WP15Y creates the readiness evidence acquisition contract and a first SXR8.DE closing-price proof-of-concept attempt.

## Result

```text
evidence_acquisition_contract_created=true
closing_price_poc_created=true
closing_price_poc_symbol=SXR8.DE
closing_price_poc_isin=IE00B5BMR087
provider_status=failed
pricing_poc_status=failed_provider_or_symbol_unavailable
limited_pricing_poc_performed=true
```

## Interpretation

The repo now has registry-to-pricing wiring, a runner, a machine artifact and a client-readable preview for SXR8.DE. The provider attempt did not return a close in the current execution environment, so no price was inserted.

## Boundary

```text
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
client_grade_claim=false
delivery_preflight_allowed=false
receipt_artifact_created=false
production_manifest_created=false
source_pdf_replaced=false
renderer_changed=false
```

## Consequence

```text
selected_next_package=ETF-EU-WP15Y-FIX
```

The next package should repair provider access or symbol mapping until one real SXR8.DE close is committed.
