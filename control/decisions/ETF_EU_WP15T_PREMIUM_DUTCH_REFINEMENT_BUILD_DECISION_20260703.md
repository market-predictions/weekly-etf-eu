# ETF-EU-WP15T premium Dutch refinement build decision

## Date

2026-07-03

## Decision

ETF-EU-WP15T creates a review-only premium visual and Dutch-first refinement candidate for the ETF EU cockpit PDF.

The candidate is stronger and more client-facing than WP15R, but it is **not** accepted as final client-grade output and does **not** reopen delivery preflight.

## Chosen architecture

```text
WP15S visual review checkpoint
→ runtime/build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate.py
→ output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf
→ output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_20260703_000000.json
→ validator/test coverage
→ control state update to ETF-EU-WP15U
```

## Stable authority rules

```text
premium_visual_refinement_candidate_created=true
dutch_first_language_refinement_candidate_created=true
review_only_refined_pdf_candidate_created=true
client_grade_status_after_wp15t=not_yet_client_grade_refined_review_only_candidate_built
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

WP15S showed that WP15R was content-complete but too technical, visually dense and English-first. WP15T addresses this with Dutch-first copy, cards, tables, evidence badges and a more sequential cockpit flow.

## Consequence

The next package is:

```text
ETF-EU-WP15U — ETF EU cockpit PDF premium Dutch refinement visual review checkpoint, no delivery
```

Delivery enablement remains blocked until a later explicit authorization records receipt/manifest authority and all required report-quality gates pass.
