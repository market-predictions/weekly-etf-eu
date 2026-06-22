# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15I — ETF EU cockpit PDF premium surface improvement decision, no delivery**.

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
```

## WP15H completion evidence

```text
WP15H=completed
review_checkpoint_created=true
review_checkpoint_decision=keep_premium_pdf_as_current_review_artifact
review_checkpoint_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
review_checkpoint_notes=output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
review_checkpoint_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py
review_checkpoint_tests=tests/test_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py
premium_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
premium_pdf_commit=fb7751026a70db355385946ee3882c68f9ec0e71
premium_surface_closeout_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
client_readability_status=acceptable_for_review_checkpoint
governance_clarity_status=acceptable_for_review_checkpoint
ucits_proxy_separation_status=acceptable_for_review_checkpoint
validation_traceability_status=acceptable_for_review_checkpoint
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
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_CLOSEOUT_OK
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_REVIEW_CHECKPOINT_OK
36 passed in 0.11s
working tree clean
```

## Active next package

```text
WP15I — ETF EU cockpit PDF premium surface improvement decision, no delivery
```

Purpose:

```text
decide whether the premium surface needs a targeted improvement iteration or can remain as the stable current review artifact, without creating production delivery authority
```

Likely inputs:

```text
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_notes_20260618_000000.md
```

WP15I should create:

```text
premium surface improvement decision artifact
premium surface improvement decision notes
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

Do not create a new PDF unless WP15I explicitly records a decision for a later separate implementation package.
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
Do not replace or delete the WP15F premium PDF evidence.
Do not replace or delete the WP15G closeout artifacts.
Do not replace or delete the WP15H review checkpoint artifacts.
