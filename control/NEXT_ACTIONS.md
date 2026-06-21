# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15G — ETF EU cockpit PDF premium surface closeout, no delivery**.

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
```

## WP15F completion evidence

```text
WP15F=completed
premium_pdf_surface_created=true
premium_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
premium_pdf_commit=fb7751026a70db355385946ee3882c68f9ec0e71
premium_pdf_renderer=tools/render_etf_eu_cockpit_pdf_premium_surface.py
premium_pdf_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface.py
premium_pdf_tests=tests/test_etf_eu_cockpit_pdf_premium_surface.py
premium_pdf_notes=output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md
original_pdf_mvp_preserved=true
layout_pdf_preserved=true
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

Codespaces validation evidence:

```text
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_RENDERED
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_OK
12 passed in 0.10s
premium PDF committed at fb7751026a70db355385946ee3882c68f9ec0e71
working tree clean
```

## Active next package

```text
WP15G — ETF EU cockpit PDF premium surface closeout, no delivery
```

Purpose:

```text
close out the committed premium PDF surface with validation evidence and explicit preservation of no-delivery and no-investment-authority boundaries
```

Likely inputs:

```text
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md
tools/render_etf_eu_cockpit_pdf_premium_surface.py
tools/validate_etf_eu_cockpit_pdf_premium_surface.py
tests/test_etf_eu_cockpit_pdf_premium_surface.py
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf
```

WP15G should create:

```text
premium surface closeout artifact
premium surface closeout notes/checklist
closeout validator/test coverage only if needed
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
Do not replace or delete the WP15F premium PDF evidence.
