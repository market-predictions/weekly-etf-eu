# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15Q — ETF EU cockpit PDF client-grade content completeness plan, no delivery**.

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
```

## ETF-EU-WP15P completion evidence

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15P
legacy_work_package_id=WP15P
status=completed
source_work_package=ETF-EU-WP15O
visual_review_checkpoint_created=true
actual_pdf_candidate_reviewed=true
source_premium_pdf_candidate_reviewed=true
source_premium_pdf_candidate_path=output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_candidate_20260618_000000.pdf
source_premium_pdf_candidate_commit=88c2a75
review_checkpoint_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_20260618_000000.json
review_checkpoint_notes=output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_notes_20260618_000000.md
review_checkpoint_validator=tools/validate_etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint.py
review_checkpoint_tests=tests/test_etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint.py
visual_review_decision=accept_as_review_only_cockpit_surface_foundation_not_delivery_grade
client_grade_status=not_yet_client_grade
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
selected_next_package=ETF-EU-WP15Q
```

## Validation evidence

```text
ETF_EU_COCKPIT_PDF_PREMIUM_VISUAL_REFINEMENT_REVIEW_CHECKPOINT_OK | selected_next_package=ETF-EU-WP15Q
12 passed in 0.13s
```

## Active next package

```text
ETF-EU-WP15Q — ETF EU cockpit PDF client-grade content completeness plan, no delivery
```

Purpose:

```text
Define the minimum client-grade content contract for the ETF EU cockpit PDF before any delivery-preflight discussion can be reconsidered.
```

## Likely inputs for ETF-EU-WP15Q

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_candidate_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint_notes_20260618_000000.md
runtime/build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate.py
```

ETF-EU-WP15Q should create:

```text
client-grade content completeness contract or plan artifact
client-grade content completeness notes
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
Do not replace the WP15O premium PDF candidate unless a later implementation package explicitly authorizes a new candidate build.
