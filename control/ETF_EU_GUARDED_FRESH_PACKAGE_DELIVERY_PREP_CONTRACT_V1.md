# ETF EU Guarded Fresh Package Delivery Prep Contract V1

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_CONTRACT_V1`

## Purpose

Define the guarded delivery-preparation layer for the MVP25 readiness-gated fresh Weekly ETF EU package.

This contract prepares explicit delivery inputs only. It does not authorize, dispatch, execute, or confirm delivery.

```text
upstream_pattern_adapted=weekly-etf guarded delivery and delivery-manifest concept; adapted for EU explicit delivery-prep without send authority
```

## Scope

MVP26 verifies the readiness-gated package and writes a non-send delivery-prep artifact around:

```text
Dutch-primary markdown
English-companion markdown
Dutch-primary HTML
English-companion HTML
Dutch-primary PDF
English-companion PDF
fresh-generation package manifest
ready-for-controlled-delivery artifact
fresh-package readiness gate
EU routine run manifest
```

The delivery-prep artifact may be used by a later explicit authorization package, but it is not itself send authority.

## Authority boundaries

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

Allowed:

```text
decision_allowed=guarded_delivery_preparation
package_readiness_gate_required=true
delivery_prep_allowed=true
delivery_execution_allowed=false
send_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
```

Not allowed:

```text
delivery_authorized=true
send_executed=true
transport_attempted=true
receipt_confirmed=true
production_delivery_authority=true
valuation_grade=true
funding_authority=true
portfolio_mutation=true
```

`ready_for_controlled_delivery=true` means package eligibility for later controlled-delivery preparation only. It is not delivery authorization, send authorization, workflow dispatch authority, or transport authority.

## Input package contract

The delivery-prep layer must use only the MVP25 readiness-gated EU package:

```text
output/fresh_generation/weekly_etf_eu_review_nl_260710.md
output/fresh_generation/weekly_etf_eu_review_260710.md
output/fresh_generation/weekly_etf_eu_review_nl_260710.html
output/fresh_generation/weekly_etf_eu_review_260710.html
output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
output/fresh_generation/weekly_etf_eu_review_260710.pdf
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
output/fresh_generation/etf_eu_fresh_package_readiness_gate_20260710_000000.json
output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

EU state references only:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
output/pricing/ucits_close_price_validation_basket_results_20260709_000000.json
```

Rejected as EU authority:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
weekly_analysis_pro_*.md as EU source truth
U.S. ETF tickers as investable EU holdings
U.S. recipient authority
U.S. delivery authority
legacy weekly-etf sender discovery as EU package authority
```

## Delivery-prep artifact contract

The delivery-prep artifact must record:

```text
schema_version=etf_eu_guarded_fresh_package_delivery_prep_v1
artifact_type=etf_eu_guarded_fresh_package_delivery_prep
ready_for_controlled_delivery=true
delivery_authorized=false
delivery_prep_created=true
delivery_prep_validated=false until validator passes in runtime
explicit_user_authorization_required=true
guarded_send_confirmation_required=true
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
send_executed=false
transport_attempted=false
transport_success=false
receipt_confirmed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
```

## Explicit authorization requirement

A future send package must require a separate explicit user instruction and a guarded-send confirmation token. MVP26 must not create that token, queue a workflow, or infer send permission from readiness.

## Guarded send confirmation requirement

Future delivery execution must require both:

```text
ready_for_controlled_delivery=true
delivery_authorized=true from a later explicit authorization package
```

MVP26 preserves:

```text
delivery_authorized=false
send_command_allowed=false
workflow_dispatch_allowed=false
run_queue_allowed=false
```

## Redaction and secrets rules

MVP26 must not read SMTP secrets, expose recipient plaintext, write raw receipt PDFs, or create any artifact containing unredacted recipient values.

```text
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
```

## Routine run manifest handoff

The EU routine run manifest must record the delivery-prep artifact path, keep transport and receipt flags false, and advance to:

```text
ETF-EU-MVP27_EXPLICIT_GUARDED_SEND_AUTHORIZATION
```

## Non-delivery guardrails

MVP26 must not:

```text
send email
dispatch workflow
create run queue file
perform live delivery
read or expose SMTP secrets
write plaintext recipient values
mutate portfolio state
promote valuation/funding/portfolio/production authority
confirm receipt for a new run
store raw Gmail PDF in GitHub
copy U.S. ETF portfolio or delivery authority
merge fresh generation and delivery into one production workflow
```
