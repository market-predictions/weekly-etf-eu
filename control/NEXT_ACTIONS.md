# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15J — ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery**.

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
```

## ETF-EU-WP15I-RECONCILE completion evidence

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15I-RECONCILE
legacy_work_package_id=WP15I
status=completed
source_work_package=WP15H
reconciles_work_package=ETF-EU-WP15I
improvement_decision_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
improvement_decision_notes=output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md
improvement_decision_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py
improvement_decision_tests=tests/test_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py
improvement_decision=create_targeted_improvement_package
decision=targeted_copy_governance_refinement_before_delivery_preflight
keep_as_current_review_artifact=true
targeted_improvement_needed=true
targeted_improvement_package_required=true
targeted_improvement_package=ETF-EU-WP15J
delivery_preflight_allowed=false
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
new_pdf_created=false
renderer_changed=false
premium_pdf_replaced=false
outbound_path_enabled=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
selected_next_package=ETF-EU-WP15J
```

Validation command set:

```text
python tools/validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
python -m pytest tests/test_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py -q
python tools/validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
python tools/validate_etf_eu_cockpit_pdf_premium_surface.py output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
```

Connector session note:

```text
validation_execution_status=not_executed_in_connector_session
```

## Active next package

```text
ETF-EU-WP15J — ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery
```

Purpose:

```text
Plan a narrow refinement that improves client-facing copy and badge language while preserving validator markers, authority boundaries and no-delivery status.
```

ETF-EU-WP15J should remain planning-only unless separately authorized.

## Likely inputs for ETF-EU-WP15J

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
```

ETF-EU-WP15J should create:

```text
narrow copy/governance refinement plan artifact
narrow copy/governance refinement plan notes
validator/test coverage if useful
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

Do not create a new PDF in ETF-EU-WP15J.
Do not render a new PDF in ETF-EU-WP15J.
Do not change the premium renderer in ETF-EU-WP15J.
Do not replace the premium PDF in ETF-EU-WP15J.
Do not start email delivery.
Do not create recipient or secrets changes.
Do not mutate portfolio state.
Do not promote candidates.
Do not create funding authority.
Do not create valuation-grade authority.
Do not fetch live data.
Do not change recommendation logic.
Do not replace or delete the original WP15A PDF evidence.
Do not replace or delete the WP15C layout PDF evidence.
Do not replace or delete the WP15E planning artifacts.
Do not replace or delete the WP15F premium PDF evidence.
Do not replace or delete the WP15G closeout artifacts.
Do not replace or delete the WP15H review checkpoint artifacts.
Do not replace or delete the ETF-EU-WP15I-RECONCILE decision artifacts.
