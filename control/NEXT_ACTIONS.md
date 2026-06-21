# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15E — ETF EU cockpit PDF MVP premium surface planning, no delivery**.

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
```

## WP15D completion evidence

```text
WP15D=completed
pdf_mvp_layout_closeout_created=true
pdf_mvp_layout_closeout_notes_created=true
pdf_mvp_layout_closeout_artifact=output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_20260618_000000.json
pdf_mvp_layout_closeout_notes=output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_notes_20260618_000000.md
pdf_mvp_layout_closeout_validator=tools/validate_etf_eu_cockpit_pdf_mvp_layout_closeout.py
pdf_mvp_layout_closeout_tests=tests/test_etf_eu_cockpit_pdf_mvp_layout_closeout.py
pdf_mvp_layout_path=output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf
pdf_mvp_layout_commit=651de79f11ded4285ca57938cfdf38d46b02e5bf
original_pdf_mvp_preserved=true
pdf_mvp_path=output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
pdf_mvp_commit=ce0146326d3235687aabd23d5e728b3ee34a8fe5
layout_improvements_confirmed=true
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
ETF_EU_COCKPIT_PDF_MVP_LAYOUT_OK
ETF_EU_COCKPIT_PDF_MVP_LAYOUT_CLOSEOUT_OK
42 passed in 0.55s
working tree clean
```

## Active next package

```text
WP15E — ETF EU cockpit PDF MVP premium surface planning, no delivery
```

Purpose:

```text
plan the premium client-grade cockpit PDF surface without enabling delivery, changing pricing evidence, or introducing investment authority
```

Likely inputs:

```text
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_mvp_layout_notes_20260618_000000.md
tools/render_etf_eu_cockpit_pdf_mvp_layout.py
tools/validate_etf_eu_cockpit_pdf_mvp_layout.py
```

WP15E should create:

```text
premium surface planning artifact
premium surface visual/layout requirements notes
minimal validator/test coverage if needed
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
