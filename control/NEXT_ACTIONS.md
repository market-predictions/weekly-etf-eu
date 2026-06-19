# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF EU pricing-line expansion for enriched cockpit candidates, no delivery**.

## Adopted strategy

```text
Keep market-predictions/weekly-etf-eu as the EU/UCITS source-of-truth repo.
Use market-predictions/weekly-etf as an upstream donor for mature implementation layers.
Port behavior, not U.S. assumptions.
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
```

## WP14P completion evidence

```text
WP14P=completed
enriched_cockpit_renderer_created=true
deterministic_renderer_created=true
render_manifest_created=true
english_rendered_cockpit_markdown_created=true
dutch_rendered_cockpit_markdown_created=true
english_rendered_cockpit_html_created=true
dutch_rendered_cockpit_html_created=true
candidate_universe_preserved=true
candidate_evidence_map_rendered=true
proxy_separation_map_rendered=true
reader_action_map_rendered=true
blocker_panel_rendered=true
debug_surface_reduced=true
ucits_identity_preserved=true
proxy_separation_preserved=true
pricing_evidence_preserved=true
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
visible_candidate_count=4
renderer_path=tools/render_etf_eu_enriched_cockpit.py
render_manifest=output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json
selected_next_package=WP14Q
selected_next_package_title=ETF EU pricing-line expansion for enriched cockpit candidates, no delivery
```

Validation evidence from WP14P local sandbox execution:

```text
python tools/render_etf_eu_enriched_cockpit.py output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json
ETF_EU_ENRICHED_COCKPIT_RENDER_CREATED | artifact=output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json | visible_candidate_count=4 | selected_next_package=WP14Q

python tools/validate_etf_eu_enriched_cockpit_render.py output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json
ETF_EU_ENRICHED_COCKPIT_RENDER_OK | artifact=output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json | visible_candidate_count=4 | selected_next_package=WP14Q

python -m pytest tests/test_etf_eu_enriched_cockpit_render.py -q
12 passed
```

Existing gates listed in the WP14P manifest remain expected gates for coordinator/Codespaces verification.

## Active next package

```text
WP14Q — ETF EU pricing-line expansion for enriched cockpit candidates, no delivery
```

Purpose:

```text
expand pricing-line evidence for the enriched cockpit candidates that are currently pricing_incomplete, identity_incomplete or blocked_until_verified, without changing delivery, portfolio, funding or valuation-grade authority
```

Likely inputs:

```text
output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json
output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
control/UCITS_SYMBOL_REGISTRY_CONTRACT.md
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json
```

WP14Q should create:

```text
pricing-line expansion artifact for enriched cockpit candidates
candidate-level pricing evidence status map
validator/test coverage for pricing-line evidence without valuation-grade authority
updated control state with delivery still blocked
```

## Delivery remains blocked until

```text
real delivery receipt/manifest path exists
explicit control-layer delivery authorization is recorded
```

## Do not do next

Do not enable production delivery.
Do not add recipients or secrets.
Do not convert pricing evidence into valuation-grade authority.
Do not promote candidates or mutate portfolio state.
Do not create funding authority.
