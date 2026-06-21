# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15C — ETF EU cockpit PDF MVP layout and readability iteration, no delivery**.

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
```

## WP15B completion evidence

```text
WP15B=completed
pdf_mvp_closeout_created=true
pdf_mvp_review_notes_created=true
pdf_mvp_closeout_artifact=output/client_surface/etf_eu_cockpit_pdf_mvp_closeout_20260618_000000.json
pdf_mvp_review_notes=output/client_surface/etf_eu_cockpit_pdf_mvp_review_notes_20260618_000000.md
pdf_mvp_closeout_validator=tools/validate_etf_eu_cockpit_pdf_mvp_closeout.py
pdf_mvp_closeout_tests=tests/test_etf_eu_cockpit_pdf_mvp_closeout.py
pdf_mvp_path=output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
pdf_mvp_commit=ce0146326d3235687aabd23d5e728b3ee34a8fe5
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

Codespaces validation evidence:

```text
ETF_EU_COCKPIT_PDF_MVP_OK
ETF_EU_COCKPIT_PDF_MVP_CLOSEOUT_OK
20 passed in 0.16s
working tree clean
```

## Active next package

```text
WP15C — ETF EU cockpit PDF MVP layout and readability iteration, no delivery
```

Purpose:

```text
improve the PDF MVP layout, readability, Dutch-first hierarchy and table presentation without enabling delivery or changing investment authority
```

Likely inputs:

```text
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_mvp_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_mvp_review_notes_20260618_000000.md
tools/render_etf_eu_cockpit_pdf_mvp.py
tools/validate_etf_eu_cockpit_pdf_mvp.py
tests/test_etf_eu_cockpit_pdf_mvp.py
output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md
output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md
```

WP15C should create:

```text
improved PDF MVP renderer or renderer iteration
updated PDF MVP output if needed
layout/readability validation notes
validator/test updates only where needed
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
