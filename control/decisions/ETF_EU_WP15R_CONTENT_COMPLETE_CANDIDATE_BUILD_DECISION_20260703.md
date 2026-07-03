# ETF-EU-WP15R content-complete cockpit PDF candidate build decision

## Date

2026-07-03

## Decision

ETF-EU-WP15R builds a review-only content-complete ETF EU cockpit PDF candidate against the WP15Q content contract.

The candidate is content-complete for review, but it is **not** client-grade delivery and does **not** reopen delivery preflight.

## Chosen architecture

```text
WP15Q content contract
→ runtime/build_etf_eu_cockpit_pdf_content_complete_candidate.py
→ output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf
→ output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_build_20260703_000000.json
→ validator/test coverage
→ control state update to ETF-EU-WP15S
```

## Stable authority rules

```text
content_complete_pdf_candidate_created=true
review_only_content_complete_candidate_created=true
visible_sections_count=12
funded_etf_holdings_count=0
client_grade_status_after_wp15r=not_yet_client_grade_review_only_candidate_built
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

WP15Q defined the required content contract, but the prior PDF candidate was still a shell. WP15R creates a PDF candidate containing the visible sections required for review: header, executive read, holdings/cash, allocation, UCITS investability, pricing/freshness, decision table, watchlist, risk context, proxy disclosure, unresolved-data block and governance footer.

## Consequence

The next package is:

```text
ETF-EU-WP15S — ETF EU cockpit PDF content-complete candidate visual review checkpoint, no delivery
```

Delivery enablement remains blocked until a later explicit authorization records receipt/manifest authority and all required report-quality gates pass.
