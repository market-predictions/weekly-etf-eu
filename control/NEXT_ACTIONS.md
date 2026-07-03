# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15T — ETF EU cockpit PDF premium visual and Dutch-first language refinement candidate, no delivery**.

## Adopted strategy

```text
Keep market-predictions/weekly-etf-eu as the EU/UCITS source-of-truth repo.
Use market-predictions/weekly-etf as an upstream donor for mature implementation layers.
Port behavior, not U.S. assumptions.
Use namespaced workpackage IDs in all repo, branch, PR, artifact and handover communication.
```

## Completed through latest package

```text
WP9
WP10
WP10B
WP11
WP12
WP12B
WP12C
WP12D
WP12E
WP12F
WP13A
WP13B
WP13C
WP13D
WP13E
WP13F
WP13G
WP13H
WP14A
WP14B
WP14C
WP14D
WP14E
WP14E-FIX
WP14F
WP14G
WP14H
WP14I
WP14J
WP14K
WP14L
WP14M
WP14N
WP14O
WP14P
WP14Q
WP14R
WP14S
WP14T
WP14U
WP15A
WP15B
WP15C
WP15D
WP15E
WP15F
WP15G
WP15H
ETF-EU-WP15I
ETF-EU-WP15I-RECONCILE
ETF-EU-WP15J
ETF-EU-WP15K
ETF-EU-WP15L
ETF-EU-WP15M
ETF-EU-WP15N
ETF-EU-WP15O
ETF-EU-WP15P
ETF-EU-WP15Q
ETF-EU-WP15R
ETF-EU-WP15S
```

## ETF-EU-WP15S completion evidence

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15S
legacy_work_package_id=WP15S
status=completed
source_work_package=ETF-EU-WP15R
source_pdf_candidate_path=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf
review_checkpoint_artifact=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_20260703_000000.json
review_checkpoint_notes=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_notes_20260703_000000.md
review_checkpoint_validator=tools/validate_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint.py
review_checkpoint_tests=tests/test_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint.py
visual_review_decision=accept_as_review_only_content_complete_foundation_request_premium_visual_and_language_refinement
content_completeness_status=content_complete_for_review_only_candidate
client_grade_status_after_wp15s=not_yet_client_grade_visual_language_refinement_required
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
selected_next_package=ETF-EU-WP15T
```

## Validation package

```text
validator_added=tools/validate_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint.py
tests_added=tests/test_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint.py
ci_status=not_visible_in_chatgpt_github_connector
```

## Active next package

```text
ETF-EU-WP15T — ETF EU cockpit PDF premium visual and Dutch-first language refinement candidate, no delivery
```

Purpose:

```text
Create a refined review-only cockpit PDF candidate with stronger client-grade visual hierarchy, Dutch-first client language, table/card structure and clearer evidence badges, while preserving no-delivery and no-authority boundaries.
```

## Likely inputs for ETF-EU-WP15T

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md
output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_20260703_000000.json
output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint_notes_20260703_000000.md
runtime/build_etf_eu_cockpit_pdf_content_complete_candidate.py
```

ETF-EU-WP15T should create:

```text
premium visual and Dutch-first language refinement PDF candidate
refinement build artifact
refinement build notes
validator/test coverage
updated control state after validation
```

## Boundary remains

```text
proof_of_concept_pdf_mvp=true
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
```

## Do not do next

Do not start email delivery.
Do not create recipient or secrets changes.
Do not create a delivery receipt.
Do not create a production delivery manifest.
Do not claim client delivery.
Do not mutate portfolio state.
Do not promote candidates.
Do not create funding authority.
Do not create valuation-grade authority.
Do not fetch live data unless a later package explicitly authorizes it.
Do not change ETF recommendation logic.
Do not replace production delivery behavior.
