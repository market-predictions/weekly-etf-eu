# ETF-EU-WP15Q client-grade content contract decision

## Date

2026-07-03

## Decision

ETF-EU-WP15Q defines the minimum client-grade content contract for the ETF EU cockpit PDF before any delivery-preflight discussion may be reconsidered.

WP15Q does **not** make the current PDF client-grade. It creates a contract and plan only.

## Chosen architecture

```text
WP15P visual review checkpoint
→ WP15Q client-grade content contract
→ WP15Q content-completeness plan artifact
→ validator/test coverage
→ control state update to ETF-EU-WP15R
```

The verified WP15Q artifacts are:

```text
control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md
output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_20260703_000000.json
output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_notes_20260703_000000.md
```

## Stable authority rules

```text
client_grade_content_contract_created=true
content_completeness_plan_created=true
client_grade_status_after_wp15q=not_yet_client_grade_contract_defined_only
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
delivery_preflight_allowed=false
outbound_path_enabled=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
```

## Reason

WP15P established that the premium PDF is visually improved but still a cockpit shell. A content-complete EU ETF PDF must define minimum decision, state, output and runbook requirements before another PDF build can credibly target client-grade quality.

## Consequence

The next package is:

```text
ETF-EU-WP15R — ETF EU cockpit PDF content-complete candidate build, no delivery
```

Delivery enablement remains blocked until a later explicit authorization records receipt/manifest authority and all required report-quality gates pass.
