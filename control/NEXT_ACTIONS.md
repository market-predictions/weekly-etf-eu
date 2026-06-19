# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF EU enriched cockpit renderer integration and quality gate, no delivery**.

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
```

## WP14O completion evidence

```text
WP14O=completed
universe_enrichment_created=true
enriched_cockpit_surface_created=true
candidate_universe_expanded=true
candidate_evidence_map_created=true
proxy_separation_map_created=true
reader_action_map_created=true
blocker_panel_created=true
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
universe_enrichment_manifest=output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json
selected_next_package=WP14P
selected_next_package_title=ETF EU enriched cockpit renderer integration and quality gate, no delivery
```

Visible candidate statuses:

```text
IE00B5BMR087=iShares Core S&P 500 UCITS ETF USD (Acc)=visible_review_candidate
IE00BMC38736=VanEck Semiconductor UCITS ETF=pricing_incomplete
TBD=iShares Physical Gold ETC=blocked_until_verified
TBD=iShares Global Infrastructure UCITS ETF=identity_incomplete
```

Validation evidence from WP14O local sandbox execution:

```text
python tools/validate_etf_eu_cockpit_universe_enrichment.py output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json
ETF_EU_COCKPIT_UNIVERSE_ENRICHMENT_OK | artifact=output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json | visible_candidate_count=4 | selected_next_package=WP14P

python -m pytest tests/test_etf_eu_cockpit_universe_enrichment.py -q
12 passed
```

Existing gates listed in the WP14O manifest remain expected gates for coordinator/Codespaces verification.

## Active next package

```text
WP14P — ETF EU enriched cockpit renderer integration and quality gate, no delivery
```

Purpose:

```text
turn the WP14O enriched UCITS universe data into a deterministic cockpit renderer / quality gate so future cockpit surfaces are generated from structured input instead of hand-built markdown and HTML
```

Likely inputs:

```text
output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json
output/client_surface/weekly_etf_eu_review_260618_cockpit_enriched.md
output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_enriched.md
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
control/UCITS_SYMBOL_REGISTRY_CONTRACT.md
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
```

WP14P should create:

```text
runtime or tool-level deterministic enriched cockpit renderer
renderer output manifest
quality gate / validator for rendered enriched cockpit outputs
pytest coverage for renderer determinism and blocked-authority flags
```

## Delivery remains blocked until

```text
real delivery receipt/manifest path exists
explicit control-layer delivery authorization is recorded
```

## Do not do next

Do not enable production delivery.
Do not add recipients or secrets.
Do not convert POC/render evidence into a delivery success claim.
Do not promote candidates or mutate portfolio state.
Do not create funding authority or valuation-grade authority.
