# Weekly ETF EU Review — Enriched Premium Cockpit POC

## Cockpit summary

- **Report status:** proof of concept / review-only.
- **Current stance:** UCITS universe is expanded for review; there is no portfolio action.
- **UCITS universe status:** four configured registry entries are visible: one verified candidate, one pricing-incomplete UCITS candidate, one blocked ETC policy case, and one identity-incomplete infrastructure candidate.
- **Main evidence gaps:** exchange-line verification, pricing-symbol coverage, ISIN completion for placeholder candidates, and policy treatment for ETC exposure.
- **Main blocker:** delivery and portfolio authority remain blocked.
- **Next product action:** integrate the enriched cockpit data into a deterministic renderer and quality gate.

## At-a-glance cards

| Card | Status | Reader meaning |
| --- | --- | --- |
| UCITS universe | Expanded | The cockpit now shows the configured S&P 500, semiconductor, gold/ETC, and infrastructure review lanes. |
| Identity evidence | Mixed | IE00B5BMR087 is verified; IE00BMC38736 is visible but still needs exchange-line hardening; two entries remain identity or policy incomplete. |
| Pricing evidence | Partial | CSPX.L and SXR8.DE retain close evidence; other candidate lines need pricing-symbol verification. |
| Proxy separation | Preserved | SPY, SMH, GLD, and PAVE remain research proxies / benchmarks only. |
| Delivery status | Blocked | No production delivery is authorized. |
| Portfolio authority | Blocked | No funding, candidate promotion, or portfolio mutation is authorized. |

## Visible UCITS universe

| Candidate | ISIN | Role | Trading lines | Research proxy | Cockpit status | Reader meaning |
| --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | Core U.S. equity exposure | CSPX.L, SXR8.DE | SPY | visible_review_candidate | First review candidate with ISIN, UCITS status, KID availability and close evidence. |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | Semiconductor thematic exposure | SMH / pricing pending | SMH | pricing_incomplete | Useful thematic candidate, but the EU exchange line and pricing symbol still need verification. |
| iShares Physical Gold ETC | TBD | Gold / hard-asset hedge | SGLN / pricing pending | GLD | blocked_until_verified | This is an ETC policy case, not a UCITS ETF; keep blocked until policy explicitly allows it. |
| iShares Global Infrastructure UCITS ETF | TBD | Infrastructure / real-asset capex exposure | INFR / pricing pending | PAVE | identity_incomplete | The lane is visible from registry/proxy mapping but needs issuer, ISIN, KID and line confirmation. |

## Candidate evidence map

| Candidate | Identity evidence | Pricing evidence | Evidence status | Evidence gaps |
| --- | --- | --- | --- | --- |
| IE00B5BMR087 | ISIN, provider, UCITS, KID, TER, benchmark and trading lines present. | CSPX.L and SXR8.DE close evidence present for 2026-06-17. | source_evidence_available | Broker line confirmation and broader weekly input integration. |
| IE00BMC38736 | ISIN, fund name, provider, UCITS wording, KID and TER present. | Pricing symbol remains pending verification. | pricing_incomplete | EU exchange line, pricing symbol, domicile, distribution and replication method. |
| iShares Physical Gold ETC | Product name and ETC nature visible. | Pricing symbol remains pending verification. | blocked_policy_case | ISIN, currency, exchange line, KID status and ETC policy authority. |
| Infrastructure UCITS placeholder | Fund name and theme visible from existing config. | Pricing symbol remains pending verification. | identity_incomplete | ISIN, issuer confirmation, KID, TER, exchange line and pricing source. |

## Pricing and identity gaps

| Gap | Affected candidates | Why it matters |
| --- | --- | --- |
| Verified daily close exists only for CSPX.L and SXR8.DE | S&P 500 UCITS candidate only | Other candidates cannot yet support the same cockpit evidence standard. |
| Pricing symbol pending | Semiconductor, gold/ETC, infrastructure | No valuation-grade or funding authority can be created from incomplete price lines. |
| ISIN missing | Gold/ETC, infrastructure | The EU model is ISIN-first; missing ISIN blocks candidate promotion. |
| Product policy unclear | Gold/ETC | ETC treatment must be decided before it can enter a UCITS-only review surface as more than a blocked policy case. |

## Proxy separation map

| U.S. proxy | EU/UCITS candidate view | Allowed use | Blocked use |
| --- | --- | --- | --- |
| SPY | IE00B5BMR087 through CSPX.L and SXR8.DE | Benchmark / research proxy | EU holding or funding source |
| SMH | VanEck Semiconductor UCITS ETF, IE00BMC38736 | Semiconductor benchmark reference | U.S. ETF holding |
| GLD | iShares Physical Gold ETC policy case | Gold reference only | UCITS holding unless ETC policy changes |
| PAVE | Infrastructure UCITS placeholder | Infrastructure research comparator | Funded candidate before identity verification |

## Reader action map

| Reader question | Cockpit answer | Action now |
| --- | --- | --- |
| What changed versus WP14N? | The cockpit data model now shows four configured review lanes instead of one visible candidate. | Review candidate coverage and gaps. |
| Which candidate has the strongest current evidence? | IE00B5BMR087 via CSPX.L and SXR8.DE. | Preserve as the evidence baseline. |
| Which candidates are interesting but incomplete? | Semiconductor, infrastructure and gold/ETC policy case. | Complete identity, pricing and policy checks. |
| What is actionable now? | Product review only. | No portfolio action. |
| What is not actionable? | Delivery, funding, valuation-grade use, candidate promotion and portfolio mutation. | Keep blocked until explicit gates change. |

## Current blockers

| Blocker | Current status | Meaning |
| --- | --- | --- |
| Delivery authority | remain_blocked | No email, no recipient activation, no production send. |
| Portfolio mutation | false | No holdings or cash changes. |
| Candidate promotion | false | No candidate is promoted to fundable status. |
| Funding authority | false | No buy/fund decision. |
| Valuation-grade authority | false | Pricing is evidence for review, not official valuation authority. |

## Appendix — Technical evidence

- Source premium cockpit manifest: `output/client_surface/etf_eu_premium_cockpit_surface_20260618_000000.json`
- Source symbol registry: `config/ucits_symbol_registry.yml`
- Source proxy map: `config/ucits_benchmark_proxy_map.yml`
- Authorization decision: `output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json`
- Validator: `tools/validate_etf_eu_cockpit_universe_enrichment.py`
- Test file: `tests/test_etf_eu_cockpit_universe_enrichment.py`
