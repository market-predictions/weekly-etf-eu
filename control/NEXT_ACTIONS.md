# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15M — ETF EU cockpit PDF targeted copy/governance renderer/PDF candidate, no delivery**.

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
WP14V_SKIP_AND_WP15A_CONTROL_REDIRECT
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
```

## ETF-EU-WP15L completion evidence

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15L
legacy_work_package_id=WP15L
status=completed
source_work_package=ETF-EU-WP15K
review_checkpoint_created=true
review_checkpoint_decision=accept_contract_refinement_and_request_scoped_renderer_pdf_candidate
implementation_review_status=accepted_as_contract_layer
renderer_pdf_candidate_required=true
review_checkpoint_artifact=output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_20260618_000000.json
review_checkpoint_notes=output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_notes_20260618_000000.md
review_checkpoint_validator=tools/validate_etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint.py
review_checkpoint_tests=tests/test_etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint.py
premium_pdf_baseline_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
premium_pdf_baseline_commit=fb7751026a70db355385946ee3882c68f9ec0e71
premium_pdf_baseline_preserved=true
validator_marker_preservation=true
ucits_proxy_separation_preserved=true
review_only_status_preserved=true
delivery_authority_preserved_as_blocked=true
new_pdf_created=false
renderer_changed=false
premium_pdf_replaced=false
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
selected_next_package=ETF-EU-WP15M
```

## Validation evidence

```text
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_TARGETED_COPY_GOVERNANCE_REFINEMENT_IMPLEMENTATION_OK | selected_next_package=ETF-EU-WP15L
ETF_EU_COCKPIT_PDF_TARGETED_COPY_GOVERNANCE_REFINEMENT_REVIEW_CHECKPOINT_OK | selected_next_package=ETF-EU-WP15M
32 passed in 0.14s
working tree clean
```

## Active next package

```text
ETF-EU-WP15M — ETF EU cockpit PDF targeted copy/governance renderer/PDF candidate, no delivery
```

Purpose:

```text
Translate the accepted copy/governance contract into a scoped review-only renderer/PDF candidate while preserving validator markers, UCITS/proxy separation, no-delivery status and blocked authority.
```

## Likely inputs for ETF-EU-WP15M

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation_notes_20260618_000000.md
```

ETF-EU-WP15M should create:

```text
scoped renderer/PDF candidate artifact
review-only PDF candidate if rendering is in scope
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
Do not mutate portfolio state.
Do not promote candidates.
Do not create funding authority.
Do not create valuation-grade authority.
Do not fetch live data.
Do not change ETF recommendation logic.
Do not replace or delete prior WP15 evidence, review, planning, reconcile or implementation artifacts.
