# Weekly ETF EU Review OS — Next Actions

Current priority: **WP15A — ETF EU cockpit first PDF MVP renderer, no delivery**.

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
```

## WP14U completion evidence

```text
WP14U=completed
coordinator_review_status=ready_for_coordinator_review
overall_readiness_status=ready_for_client_surface_review
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

Codespaces validation evidence:

```text
ETF_EU_COCKPIT_POC_COORDINATOR_CLOSEOUT_OK
11 passed in 0.11s
working tree clean
```

## Review-loop redirect

```text
WP14V=skipped
skip_reason=avoid_review_loop_after_validated_poc_closeout
selected_next_package=WP15A
selected_next_package_title=ETF EU cockpit first PDF MVP renderer, no delivery
```

The project is intentionally exiting the review-loop after WP14U and routing to the first minimum viable PDF output.

## Active next package

```text
WP15A — ETF EU cockpit first PDF MVP renderer, no delivery
```

Purpose:

```text
create the first PDF output from the validated cockpit proof-of-concept package while preserving review-only status and all blocked authority flags
```

Target output:

```text
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
```

Expected support files:

```text
tools/render_etf_eu_cockpit_pdf_mvp.py
tools/validate_etf_eu_cockpit_pdf_mvp.py
tests/test_etf_eu_cockpit_pdf_mvp.py
```

Expected inputs:

```text
output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_poc_package_20260618_000000.json
output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.html
output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.html
output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md
output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md
```

## Boundary remains

```text
first_pdf_mvp_not_yet_implemented=true
pdf_mvp_is_not_production_delivery=true
pdf_mvp_does_not_authorize_sending_reports=true
pdf_mvp_does_not_authorize_portfolio_mutation=true
pdf_mvp_does_not_authorize_candidate_promotion=true
pdf_mvp_does_not_authorize_funding=true
pdf_mvp_does_not_create_valuation_grade_authority=true
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```
