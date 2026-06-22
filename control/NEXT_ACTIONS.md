# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15J — ETF EU cockpit PDF evidence archive and roadmap checkpoint, no delivery**.

## Adopted strategy

```text
Keep market-predictions/weekly-etf-eu as the EU/UCITS source-of-truth repo.
Use market-predictions/weekly-etf as an upstream donor for mature implementation layers.
Port behavior, not U.S. assumptions.
```

## Completed through latest validated package

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
WP15I
```

## WP15I completion evidence

```text
WP15I=completed
improvement_decision_created=true
improvement_decision=keep_current_premium_surface
improvement_decision_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
improvement_decision_notes=output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md
improvement_decision_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py
improvement_decision_tests=tests/test_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py
premium_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
premium_pdf_commit=fb7751026a70db355385946ee3882c68f9ec0e71
review_checkpoint_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
targeted_improvement_package_required=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
new_pdf_created=false
renderer_changed=false
premium_pdf_replaced=false
```

Codespaces validation evidence:

```text
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_OK
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_REVIEW_CHECKPOINT_OK
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_IMPROVEMENT_DECISION_OK
37 passed in 0.29s
working tree clean
```

## Active next package

```text
WP15J — ETF EU cockpit PDF evidence archive and roadmap checkpoint, no delivery
```

Purpose:

```text
archive the premium PDF evidence chain and checkpoint the roadmap so future work can move away from repeated renderer/review loops toward the next controlled roadmap decision
```

Likely inputs:

```text
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
```

WP15J should create:

```text
premium PDF evidence archive artifact
premium PDF roadmap checkpoint notes
validator/test coverage if needed
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

Do not create a new PDF.
Do not render a new PDF.
Do not change the premium renderer.
Do not replace the premium PDF.
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
Do not replace or delete the WP15I improvement decision artifacts.
