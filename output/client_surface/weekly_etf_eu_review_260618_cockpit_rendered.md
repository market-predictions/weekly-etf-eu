# Weekly ETF EU Review — Rendered Enriched Cockpit POC

## Cockpit summary

- **Report status:** proof of concept / review-only.
- **Current stance:** the enriched UCITS cockpit is generated deterministically from structured input; there is no portfolio action.
- **UCITS universe status:** 4 visible review lanes are rendered from the enrichment manifest.
- **Main evidence gaps:** pricing-symbol coverage, exchange-line verification, ISIN completion and product-policy treatment for ETC exposure.
- **Main blocker:** delivery, funding, valuation-grade use, candidate promotion and portfolio mutation remain blocked.
- **Next product action:** expand pricing-line evidence for enriched cockpit candidates.

## At-a-glance cards

| Card | Status | Reader meaning |
| --- | --- | --- |
| UCITS universe | Rendered | 4 structured candidates are visible in the cockpit. |
| Identity evidence | Mixed | ISIN-first identity is preserved; incomplete lanes remain marked. |
| Pricing evidence | Partial | CSPX.L and SXR8.DE retain pricing evidence; other lines remain pending. |
| Proxy separation | Preserved | SPY, SMH, GLD and PAVE are research proxies / benchmarks only. |
| Delivery status | Blocked | delivery_authorization_decision=remain_blocked. |
| Portfolio authority | Blocked | production_delivery=false; portfolio_mutation=false; candidate_promotion=false; funding_authority=false; valuation_grade=false. |

## Visible UCITS universe

| Candidate | ISIN | Provider | UCITS status | Trading lines | Research proxy | Cockpit status |
| --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | iShares / BlackRock | confirmed | CSPX.L (USD, London Stock Exchange), SXR8.DE (EUR, Xetra) | SPY | visible_review_candidate |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | VanEck | confirmed_by_fund_name | pending_verification (USD, primary_line_pending_verification) | SMH | pricing_incomplete |
| iShares Physical Gold ETC | TBD | iShares / BlackRock | not_ucits_etc | pending_verification (pending_verification, pending_verification) | GLD | blocked_until_verified |
| iShares Global Infrastructure UCITS ETF | TBD | iShares / BlackRock | pending_verification | pending_verification (pending_verification, pending_verification) | PAVE | identity_incomplete |

## Candidate evidence map

| Candidate | Identity evidence | Pricing evidence | Evidence status | Evidence gaps |
| --- | --- | --- | --- | --- |
| IE00B5BMR087 / iShares Core S&P 500 UCITS ETF USD (Acc) | UCITS=confirmed; KID=available; benchmark=S&P 500 Index | CSPX.L, SXR8.DE | source_evidence_available | broker_line_confirmation, weekly_input_integration |
| IE00BMC38736 / VanEck Semiconductor UCITS ETF | UCITS=confirmed_by_fund_name; KID=available; benchmark=semiconductor_equity_basket | pending_verification | pricing_incomplete | eu_exchange_line, pricing_symbol_yahoo, domicile, distribution_policy, replication_method |
| TBD / iShares Physical Gold ETC | UCITS=not_ucits_etc; KID=pending_verification; benchmark=LBMA gold price reference | pending_verification | blocked_policy_case | isin, trading_currency, exchange_line, kid_status, etc_policy_authority |
| TBD / iShares Global Infrastructure UCITS ETF | UCITS=pending_verification; KID=pending_verification; benchmark=FTSE Global Core Infrastructure reference_pending_verification | pending_verification | identity_incomplete | isin, issuer_confirmation, kid_status, ter, exchange_line, pricing_source |

## Pricing and identity gaps

| Gap | Affected area | Why it matters |
| --- | --- | --- |
| Pricing symbols pending | Semiconductor, gold/ETC and infrastructure lanes | These lanes cannot become valuation-grade evidence until pricing lines are verified. |
| ISIN placeholders | Gold/ETC and infrastructure lanes | ISIN-first identity is mandatory before candidate promotion. |
| ETC policy treatment | Gold/ETC lane | The gold case remains blocked until policy authority explicitly allows it. |

## Proxy separation map

| U.S. proxy | Rendered EU/UCITS view | Allowed use | Blocked use |
| --- | --- | --- | --- |
| SPY | iShares Core S&P 500 UCITS ETF USD (Acc) / IE00B5BMR087 | benchmark / research proxy only | EU holding, funding source, or portfolio position |
| SMH | VanEck Semiconductor UCITS ETF / IE00BMC38736 | benchmark / research proxy only | EU holding, funding source, or portfolio position |
| GLD | iShares Physical Gold ETC / TBD | benchmark / research proxy only | EU holding, funding source, or portfolio position |
| PAVE | iShares Global Infrastructure UCITS ETF / TBD | benchmark / research proxy only | EU holding, funding source, or portfolio position |

## Reader action map

| Reader question | Cockpit answer | Action now |
| --- | --- | --- |
| What changed? | The cockpit is generated from structured input. | Review render determinism. |
| Which candidate has strongest evidence? | IE00B5BMR087 via CSPX.L and SXR8.DE. | Preserve this as the evidence baseline. |
| What stays blocked? | Delivery, funding, valuation-grade use, candidate promotion and portfolio mutation. | Keep blocked. |

## Current blockers

| Blocker | Current status | Meaning |
| --- | --- | --- |
| Delivery authority | delivery_authorization_decision=remain_blocked | No email, no recipient activation, no production send. |
| Production delivery | production_delivery=false | No report delivery is enabled. |
| Portfolio mutation | portfolio_mutation=false | No holdings or cash changes. |
| Candidate promotion | candidate_promotion=false | No candidate is promoted. |
| Funding authority | funding_authority=false | No buy or funding decision. |
| Valuation-grade authority | valuation_grade=false | Pricing remains review evidence only. |

## Appendix — Technical evidence

- Source universe enrichment manifest: `output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json`
- Render manifest: `output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json`
- Renderer: `tools/render_etf_eu_enriched_cockpit.py`
- Validator: `tools/validate_etf_eu_enriched_cockpit_render.py`
- Test file: `tests/test_etf_eu_enriched_cockpit_render.py`
