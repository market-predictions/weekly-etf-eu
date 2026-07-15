# Weekly ETF EU Client-Grade Report Roadmap

Date: 2026-07-15
Status: active fast-track implementation
Workstream: `ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2`

## Objective

Move the Weekly ETF EU product from a technically clean UCITS verification memo to a premium client-grade decision report, using `market-predictions/weekly-etf` as the architectural donor while preserving EU/UCITS authority.

This roadmap is executed as one integrated preview stream. It does not require separate permission for each internal phase.

## Operating rule

```text
weekly-etf donor architecture
→ EU-specific normalized report state
→ conditional portfolio analytics
→ macro/opportunity decision surfaces
→ component-based client renderer
→ proportionate product-quality validation
→ one preview review
→ explicit promotion decision
```

Do not copy U.S. holdings, U.S. instrument authority, U.S. recipient authority or U.S. funding assumptions.

## Phase 1 — Premium EU report contract

Create two coherent client surfaces in one PDF.

### Investor brief

1. Executive cockpit
2. Portfolio action and capital
3. Regime and policy dashboard
4. Structural UCITS opportunity radar
5. Key risks and invalidations
6. Portfolio development
7. Conclusion

### Analyst appendix

8. Allocation map
9. Second-order effects
10. UCITS candidate and pricing evidence
11. Verification funnel
12. Current positions — conditional
13. Replacement and rotation analysis — conditional
14. Input for the next run
15. Disclaimer

Target length: 6–12 pages depending on available state. Do not manufacture empty sections merely to increase page count.

## Phase 2 — Normalized EU runtime report state

Build a single run-scoped JSON artifact from:

- EU portfolio state
- EU valuation history
- current UCITS pricing artifact
- UCITS symbol registry
- current macro policy pack
- candidate/watchlist and investability evidence

The runtime state is the only input to the v2 renderer. Markdown and prior PDFs are not state authority.

## Phase 3 — Valuation history and equity curve

Adapt the donor SVG equity-curve contract.

Rules:

- append or consume validated EU valuation observations only;
- reconcile the final point to current NAV;
- show a graph only when at least two meaningful observations exist;
- when the model is still cash-only with no meaningful NAV movement, show a clear cash-preservation callout instead of a decorative flat graph;
- activate the graph automatically after meaningful portfolio history exists.

## Phase 4 — Macro, opportunity and decision layers

Adapt the donor macro and decision-surface concepts for the EU product:

- regime summary with freshness disclosure;
- ECB/Fed policy context only when the macro artifact is sufficiently fresh;
- structural UCITS opportunity radar;
- allocation map;
- second-order effects;
- verification funnel;
- downside-risk and avoidance radar instead of a literal leveraged/inverse short-product recommendation surface.

U.S. ETFs remain benchmark or research references only.

## Phase 5 — Component-based premium renderer

Create a portrait A4 renderer with:

- premium masthead;
- investor-report and analyst-appendix separation;
- executive summary cards;
- numbered section badges;
- reusable panels and callouts;
- branded tables;
- deterministic SVG chart support;
- print-aware pagination;
- Dutch-primary and English-companion parity.

The current production renderer remains intact until explicit promotion.

## Phase 6 — Proportionate product-quality validation

Validate only material product contracts:

- required investor and analyst sections;
- clean Dutch and English client language;
- ISIN-first identity;
- U.S. proxies labelled research-only;
- no internal workflow or authority metadata;
- semantic tables;
- chart/cash-callout conditional correctness;
- readable PDF pagination;
- reasonable page count;
- no clipping or raw Markdown leakage.

Do not create a large gate hierarchy or repeated approval loop. One automated preview pass and one final side-by-side client review are sufficient before promotion.

## Delivery boundary

This workstream is preview-only.

```text
portfolio_mutation=false
transport_attempted=false
send_executed=false
receipt_check_performed=false
production_renderer_replaced=false
```

## Promotion rule

After the integrated preview passes automated validation and side-by-side review against the donor report, make one explicit decision:

- promote v2 into routine production; or
- record a short, concrete defect list and repair only those defects.

Do not restart architecture planning unless a specific structural defect is found.
