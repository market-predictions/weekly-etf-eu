# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15F — ETF EU cockpit PDF premium surface implementation, no delivery**.

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
WP13I
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
```

## WP15E completion evidence

```text
WP15E=completed
premium_surface_planning_created=true
premium_surface_markdown_plan=output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
premium_surface_json_plan=output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.json
premium_surface_plan_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface_plan.py
premium_surface_plan_tests=tests/test_etf_eu_cockpit_pdf_premium_surface_plan.py
original_pdf_mvp_preserved=true
layout_pdf_preserved=true
planning_only=true
new_pdf_created=false
renderer_changed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
live_data_fetch_performed=false
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

Codespaces validation evidence:

```text
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_PLAN_OK
12 passed in 0.05s
working tree clean
```

## Active next package

```text
WP15F — ETF EU cockpit PDF premium surface implementation, no delivery
```

Purpose:

```text
implement the planned premium client-grade cockpit PDF surface while preserving proof-of-concept status, no-delivery boundary, and no investment authority changes
```

Likely inputs:

```text
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.json
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf
tools/render_etf_eu_cockpit_pdf_mvp_layout.py
tools/validate_etf_eu_cockpit_pdf_mvp_layout.py
```

WP15F should create:

```text
premium PDF renderer implementation
premium PDF output artifact
premium PDF validator and tests
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
Do not change recommendation logic.
Do not create another review-feedback package.
Do not replace or delete the original WP15A PDF evidence.
Do not replace or delete the WP15C layout PDF evidence.
