# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15AI — ETF EU PRIIPs/KID and liquidity/spread investability evidence**.

## Latest completion

```text
work_package_id=ETF-EU-WP15AH
status=completed
source_work_package=ETF-EU-WP15AG
pricing_freshness_policy_created=true
valuation_reconciliation_policy_created=true
pricing_freshness_policy_validated=true
valuation_reconciliation_policy_validated=true
readiness_gate_status=pricing_and_valuation_policy_defined_not_client_grade
accepted_review_only_foundation=true
resolved_policy_gaps_count=2
remaining_client_grade_blockers_count=6
remaining_delivery_preflight_blockers_count=8
pdf_exists=true
pdf_page_count=4
successful_rows_count=2
failed_rows_count=0
skipped_rows_count=1
first_successful_symbol=SXR8.DE
first_successful_close_date=2026-07-03
first_successful_close=706.119995
first_successful_freshness_policy_status=current_completed_session
second_successful_symbol=CSPX.L
second_successful_close_date=2026-07-03
second_successful_close=807.859985
second_successful_freshness_policy_status=current_completed_session
smh_status=skipped_pending_registry_status
smh_freshness_policy_status=unpriced_or_pending_verification
review_only=true
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
delivery_preflight_allowed=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
live_price_fetch_performed=false
pricing_evidence_changed=false
new_pdf_created=false
renderer_changed=false
selected_next_package=ETF-EU-WP15AI
```

## Active next package

```text
ETF-EU-WP15AI — ETF EU PRIIPs/KID and liquidity/spread investability evidence
```

Purpose:

```text
Acquire and validate PRIIPs/KID availability and liquidity/spread evidence for relevant UCITS trading lines without fetching new close prices, mutating portfolio state, enabling delivery, or creating client-grade authority.
```

## Scope guardrails

```text
Do not fetch new close prices.
Do not mutate portfolio state.
Do not enable delivery-preflight.
Do not create client-grade authority.
Do not create valuation-grade authority.
Do not regenerate or replace the PDF.
Do not change recommendation logic.
Do not change SMTP, secrets, recipients, delivery receipts, or production manifests.
```
