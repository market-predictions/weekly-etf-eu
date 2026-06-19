# Weekly ETF EU Review — Premium Cockpit POC

## Cockpit summary

- **Report status:** proof of concept / review-only.
- **Current stance:** UCITS surface is visible; there is no portfolio action.
- **UCITS evidence:** IE00B5BMR087 is visible through CSPX.L and SXR8.DE.
- **Main blocker:** delivery and portfolio authority remain blocked.
- **Next product action:** improve the cockpit and expand the UCITS universe.

## At-a-glance cards

| Card | Status | Reader meaning |
| --- | --- | --- |
| UCITS visibility | Visible | The first UCITS candidate is clearly shown with ISIN and exchange lines. |
| Pricing evidence | Present | Close evidence exists for CSPX.L and SXR8.DE. |
| Research proxies | Separated | SPY is benchmark / research proxy only, not an EU holding. |
| Delivery status | Blocked | No production delivery is authorized. |
| Portfolio authority | Blocked | No funding, candidate promotion, or portfolio mutation is authorized. |

## Visible UCITS candidate

| Fund | ISIN | Trading line | Currency | Reader use |
| --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF | IE00B5BMR087 | CSPX.L | USD | UCITS candidate visibility and price-line evidence. |
| iShares Core S&P 500 UCITS ETF | IE00B5BMR087 | SXR8.DE | EUR | EUR trading-line visibility for Dutch/EU review. |

## Pricing evidence

| Pricing symbol | Close date | Close | Currency | Status |
| --- | --- | ---: | --- | --- |
| CSPX.L | 2026-06-17 | 809.24 | USD | Source evidence available. |
| SXR8.DE | 2026-06-17 | 698.02 | EUR | Source evidence available. |

This pricing evidence supports the cockpit view, but it does not create valuation-grade authority.

## Proxy separation

SPY remains a benchmark and research proxy only. It can help compare U.S. S&P 500 behavior with the UCITS candidate, but it is not an EU investable holding in this report.

## Reader action map

| Reader question | Cockpit answer | Action now |
| --- | --- | --- |
| What is the ETF EU status? | Proof of concept, review-only. | Review the cockpit layout and evidence clarity. |
| Which UCITS candidate is visible? | IE00B5BMR087 through CSPX.L and SXR8.DE. | Check ISIN, trading line, currency, and close evidence. |
| What is actionable now? | Product review only. | No portfolio action. |
| What is not actionable? | Delivery, funding, valuation-grade use, and candidate promotion. | Keep blocked until explicit gates change. |
| What should I look at first? | UCITS identity, price evidence, and proxy separation. | Use these panels before reading the appendix. |

## Current blockers

| Blocker | Current status | Meaning |
| --- | --- | --- |
| Delivery authority | remain_blocked | No email, no recipient activation, no production send. |
| Portfolio mutation | false | No holdings or cash changes. |
| Funding authority | false | No buy/fund decision. |
| Valuation-grade authority | false | Pricing is evidence for review, not official valuation authority. |
| UCITS universe breadth | limited | The next package should expand the UCITS universe and enrich cockpit data. |

## Appendix — Technical evidence

- Source client-surface manifest: `output/client_surface/etf_eu_client_surface_20260618_000000.json`
- Source English client surface: `output/client_surface/weekly_etf_eu_review_260618_client_surface.md`
- Source Dutch client surface: `output/client_surface/weekly_etf_eu_review_nl_260618_client_surface.md`
- Authorization decision: `output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json`
- Validator: `tools/validate_etf_eu_premium_cockpit_surface.py`
- Test file: `tests/test_etf_eu_premium_cockpit_surface.py`
