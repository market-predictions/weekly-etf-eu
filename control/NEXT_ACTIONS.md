# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF EU cockpit pricing evidence integration, no delivery**.

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
WP14Q
```

## WP14Q completion evidence

```text
WP14Q=completed
pricing_line_expansion_created=true
candidate_pricing_evidence_map_created=true
pricing_line_status_map_created=true
proxy_ambiguity_guard_created=true
valuation_grade_guard_created=true
funding_authority_guard_created=true
candidate_promotion_guard_created=true
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
pricing_line_expansion_manifest=output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json
pricing_line_expansion_notes=output/pricing/etf_eu_pricing_line_expansion_notes_20260618_000000.md
selected_next_package=WP14R
selected_next_package_title=ETF EU cockpit pricing evidence integration, no delivery
```

Pricing-line evidence summary:

```text
CSPX.L=current_review_only_baseline
SXR8.DE=current_review_only_baseline
SMH=ambiguous_or_pending_not_safe_ucits_pricing_evidence
GLD=research_proxy_only_not_eu_holding
PAVE=research_proxy_only_not_eu_holding
```

Validation evidence from WP14Q local sandbox mirror execution:

```text
python tools/validate_etf_eu_pricing_line_expansion.py output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json
ETF_EU_PRICING_LINE_EXPANSION_OK | artifact=output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json | visible_candidate_count=4 | selected_next_package=WP14R

python -m pytest tests/test_etf_eu_pricing_line_expansion.py -q
10 passed in local sandbox mirror
```

Existing gates listed in the WP14Q manifest remain expected gates for coordinator/Codespaces verification.

## Active next package

```text
WP14R — ETF EU cockpit pricing evidence integration, no delivery
```

Purpose:

```text
integrate the WP14Q pricing-line evidence map into the enriched cockpit surface and renderer output without changing delivery, portfolio, funding, candidate promotion or valuation-grade authority
```

Likely inputs:

```text
output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json
output/pricing/etf_eu_pricing_line_expansion_notes_20260618_000000.md
output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json
output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
control/UCITS_SYMBOL_REGISTRY_CONTRACT.md
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json
```

WP14R should create:

```text
cockpit pricing evidence integration artifact
updated/rendered cockpit surface that includes pricing evidence status map
validator/test coverage for pricing evidence integration and authority guards
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
Do not treat SMH, GLD or PAVE as safe EU pricing lines.
