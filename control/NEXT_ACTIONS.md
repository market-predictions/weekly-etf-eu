# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15K — ETF EU cockpit PDF premium surface targeted copy/governance refinement implementation, no delivery**.

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
```

## ETF-EU-WP15J completion evidence

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15J
legacy_work_package_id=WP15J
status=completed
source_work_package=ETF-EU-WP15I-RECONCILE
targeted_refinement_plan_created=true
targeted_refinement_plan_decision=plan_future_copy_governance_refinement
implementation_in_this_package=false
targeted_refinement_plan_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_20260618_000000.json
targeted_refinement_plan_notes=output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_notes_20260618_000000.md
targeted_refinement_plan_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan.py
targeted_refinement_plan_tests=tests/test_etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan.py
premium_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
premium_pdf_commit=fb7751026a70db355385946ee3882c68f9ec0e71
premium_pdf_preserved=true
improvement_decision=create_targeted_improvement_package
targeted_improvement_package_required=true
targeted_improvement_package=ETF-EU-WP15J
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
delivery_preflight_allowed=false
new_pdf_created=false
renderer_changed=false
premium_pdf_replaced=false
outbound_path_enabled=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
selected_next_package=ETF-EU-WP15K
```

Validation evidence:

```text
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_IMPROVEMENT_DECISION_OK | selected_next_package=ETF-EU-WP15J
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_TARGETED_COPY_GOVERNANCE_REFINEMENT_PLAN_OK | selected_next_package=ETF-EU-WP15K
29 passed in 0.08s
working tree clean
```

## Active next package

```text
ETF-EU-WP15K — ETF EU cockpit PDF premium surface targeted copy/governance refinement implementation, no delivery
```

Purpose:

```text
Implement the narrow copy/governance refinement planned in ETF-EU-WP15J while preserving validator markers, authority boundaries and no-delivery status.
```

ETF-EU-WP15K must remain no-delivery unless separately authorized.

## Likely inputs for ETF-EU-WP15K

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
```

ETF-EU-WP15K should create:

```text
narrow copy/governance refinement implementation artifact
updated renderer/copy contract only if scoped and deterministic
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
Do not replace or delete the original WP15A PDF evidence.
Do not replace or delete the WP15C layout PDF evidence.
Do not replace or delete the WP15E planning artifacts.
Do not replace or delete the WP15F premium PDF evidence.
Do not replace or delete the WP15G closeout artifacts.
Do not replace or delete the WP15H review checkpoint artifacts.
Do not replace or delete the ETF-EU-WP15I-RECONCILE decision artifacts.
Do not replace or delete the ETF-EU-WP15J planning artifacts.
