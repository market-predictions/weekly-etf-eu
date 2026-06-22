# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15I — ETF EU cockpit PDF premium surface copy/governance refinement plan, no delivery**.

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
premium_surface_review_checkpoint_created=true
premium_surface_review_checkpoint_notes_created=true
premium_surface_review_checkpoint_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
premium_surface_review_checkpoint_notes=output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
premium_surface_review_checkpoint_validator=tools/validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py
premium_surface_review_checkpoint_tests=tests/test_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py
reviewed_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
source_closeout_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
review_checkpoint_result=acceptable_as_review_evidence_not_delivery_ready
client_readability_result=improved_and_understandable_for_review_context_but_not_final_client_surface
governance_result=authority_boundaries_preserved
product_checkpoint_result=premium_surface_is_better_than_mvp_layout_and_should_be_preserved_as_evidence
selected_next_package=WP15I
```

Validation commands to run:

```text
python tools/validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
python -m pytest tests/test_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py -q
python tools/validate_etf_eu_cockpit_pdf_premium_surface.py output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
python tools/validate_etf_eu_cockpit_pdf_premium_surface_closeout.py output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
```

Expected validation markers:

```text
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_REVIEW_CHECKPOINT_OK
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_OK
ETF_EU_COCKPIT_PDF_PREMIUM_SURFACE_CLOSEOUT_OK
```

## Active next package

```text
WP15I — ETF EU cockpit PDF premium surface copy/governance refinement plan, no delivery
```

Purpose:

```text
Define a small, no-delivery refinement plan that separates final client-facing copy from validator/debug markers, without rendering a new PDF or changing delivery authority.
```

Likely inputs:

```text
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
```

WP15I should create:

```text
copy/governance refinement plan artifact
human-readable refinement plan notes
explicit client-copy versus machine-marker distinction
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
Do not create a delivery-preflight implementation package yet.
Do not replace or delete the original WP15A PDF evidence.
Do not replace or delete the WP15C layout PDF evidence.
Do not replace or delete the WP15F premium PDF evidence.
