# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-06-19

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Current phase

```text
Phase 9 — EU product assembly via donor-port strategy
```

## Core boundary

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
ready_for_wp13_preflight_only=true
wp13_authority=false
wp14_authority=false
```

## Strategic authority

`weekly-etf-eu` remains the EU/UCITS source-of-truth repo. `weekly-etf` remains a donor for mature implementation patterns only.

```text
Port behavior, not U.S. assumptions.
```

## Closed packages

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
```

## Latest completed package — WP14R

```text
WP14R=completed
pricing_integration_created=true
pricing_integrated_cockpit_surface_created=true
pricing_line_evidence_rendered=true
candidate_pricing_evidence_preserved=true
pricing_line_status_map_preserved=true
unsafe_pricing_symbol_guard_rendered=true
proxy_ambiguity_guard_rendered=true
valuation_grade_guard_rendered=true
funding_authority_guard_rendered=true
candidate_promotion_guard_rendered=true
ucits_identity_preserved=true
proxy_separation_preserved=true
pricing_evidence_preserved=true
debug_surface_reduced=true
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
visible_candidate_count=4
pricing_integrated_renderer=tools/render_etf_eu_pricing_integrated_cockpit.py
pricing_integration_manifest=output/client_surface/etf_eu_cockpit_pricing_integration_20260618_000000.json
english_pricing_integrated_cockpit_markdown_path=output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md
dutch_pricing_integrated_cockpit_markdown_path=output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md
english_pricing_integrated_cockpit_html_path=output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.html
dutch_pricing_integrated_cockpit_html_path=output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.html
pricing_integration_validator=tools/validate_etf_eu_cockpit_pricing_integration.py
pricing_integration_tests=tests/test_etf_eu_cockpit_pricing_integration.py
selected_next_package=WP14S
selected_next_package_title=ETF EU cockpit client-surface readiness gate, no delivery
```

Pricing-line evidence integrated into the cockpit:

```text
IE00B5BMR087=iShares Core S&P 500 UCITS ETF USD (Acc)=source_evidence_available=usable_for_review_only=CSPX.L/SXR8.DE baseline
IE00BMC38736=VanEck Semiconductor UCITS ETF=pricing_symbol_ambiguous=not_safe_until_exchange_specific_ucits_line_verified
TBD=iShares Physical Gold ETC=policy_blocked=not_safe_until_etc_policy_decision
TBD=iShares Global Infrastructure UCITS ETF=identity_incomplete=not_safe_until_isin_and_issuer_verified
```

Authority and proxy guards preserved:

```text
SPY=research_proxy_only
SMH=research_proxy_only_and_ambiguous_as_pricing_symbol
GLD=research_proxy_only_not_eu_holding
PAVE=research_proxy_only_not_eu_holding
safe_for_valuation_grade=false_for_all_candidates
safe_for_funding_decision=false_for_all_candidates
safe_for_candidate_promotion=false_for_all_candidates
```

Validation evidence from WP14R local sandbox mirror execution:

```text
python tools/render_etf_eu_pricing_integrated_cockpit.py output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json
ETF_EU_COCKPIT_PRICING_INTEGRATION_CREATED | artifact=output/client_surface/etf_eu_cockpit_pricing_integration_20260618_000000.json | visible_candidate_count=4 | selected_next_package=WP14S

python tools/validate_etf_eu_cockpit_pricing_integration.py output/client_surface/etf_eu_cockpit_pricing_integration_20260618_000000.json
ETF_EU_COCKPIT_PRICING_INTEGRATION_OK | artifact=output/client_surface/etf_eu_cockpit_pricing_integration_20260618_000000.json | visible_candidate_count=4 | selected_next_package=WP14S

python -m pytest tests/test_etf_eu_cockpit_pricing_integration.py -q
15 passed in local sandbox mirror
```

Existing gates listed in the WP14R manifest remain expected gates for coordinator/Codespaces verification.

## Active product roadmap

```text
WP14S — ETF EU cockpit client-surface readiness gate, no delivery
Delivery enablement — blocked until explicit receipt/manifest authority
```

## Immediate next action

Start WP14S.

Goal:

```text
validate the pricing-integrated cockpit as a client-surface readiness gate while preserving review-only status and blocked delivery authority
```

## Boundary rule

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
ready_for_wp13_preflight_only=true
wp13_authority=false
wp14_authority=false
```
