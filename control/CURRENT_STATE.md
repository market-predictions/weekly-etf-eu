# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-06-04

## Repository identity

```text
market-predictions/weekly-etf-eu
```

This repository is the European / Dutch-client UCITS ETF review environment. It is derived from `market-predictions/weekly-etf`, but it is not a translated copy of the U.S. ETF model.

Current product goal:

```text
Dutch/EU-client ETF review using UCITS ETFs as investable instruments.
```

The original `market-predictions/weekly-etf` repository remains the U.S.-ETF model baseline. Inherited U.S. files in this repository are historical clone artifacts unless explicitly re-authorized for the EU/UCITS product.

## Four-layer operating model

Always keep these layers separate:

1. **Decision framework** — which UCITS ETFs available to Dutch/EU investors deserve capital.
2. **Input/state contract** — where UCITS identity, investability, pricing, portfolio and delivery facts come from.
3. **Output contract** — how Dutch-first EU reports distinguish investable UCITS ETFs from U.S. research proxies.
4. **Operational runbook** — how workflows and scripts execute validation, pricing, reporting and delivery without accidental U.S. ETF portfolio authority.

## Current phase

```text
Phase 6 — agreement-aware pricing surface exists; non-production shadow verification pending
```

The repo has moved beyond the M1 adapter layer. Source metadata, the agreement gate, the agreement-aware valuation bridge, pricing-surface report wrapper, fundability promotion contract and non-production shadow workflow are now present.

The shadow workflow must still be treated as **pending verification** until GitHub Actions status or a committed validation evidence artifact proves success.

## Completed baseline milestones

- repository created and mirror-pushed from `weekly-etf`;
- EU/UCITS control layer created;
- UCITS authority files and config stubs added;
- EU cash-only state files added;
- no-U.S.-ETF-as-EU-holding validator added;
- inherited U.S. production send workflow disabled for EU use;
- EU bootstrap validation workflow added and previously validated;
- EU output contract and output validator added;
- Dutch-first and English companion cash-only report skeleton added;
- UCITS candidate registry seeded;
- UCITS registry and investability validators added;
- UCITS pricing-line contract, candidate extractor and preflight path added;
- valuation-pricing authority contract, source policy, builder and validator added;
- M0 ground-clearing integrated;
- M1 typed `PriceSource` / `PriceResult` pricing spine integrated;
- M1 Stooq, Börse Frankfurt / Xetra, Yahoo fallback and issuer NAV adapters integrated.

## Recent completed integrations

| Item | Status | Evidence / commit | Authority result |
|---|---:|---|---|
| PR `#8` source metadata policy | completed | `270446ee54d7f97223b2b94f6207ec2b7c88de22` | metadata classification only |
| PR `#9` agreement gate | completed | `575f919614690a3a851dc4968dea0cfe3a1a870d` | classifies evidence as `valuation_grade`, `provisional`, or `blocked`; no funding |
| PR `#10` valuation agreement bridge | completed as wrapper bridge | `51f91751e8df19bc5879b4a6ee4c3280e663c55e` | agreement evidence attached without valuation promotion |
| Pricing-surface wrapper | completed | wrapper files recorded in `control/WORKFLOW_WRAPPER_WIRING_DECISION_20260604.md` | report surface only; evidence-only |
| Fundability promotion contract | completed | `46615795029311920f6a3d3a7cf8e91c668a174e` plus tests `3675b57072093dbad8144931c11b7f114d860c77` | defines gates; does not promote |
| Shadow workflow created | completed as non-production workflow | `03e7b539b8bc26c746db51c1db383f728e773e71`, queue trigger update `4b458a30405958b06e833bdb4de73cabf48c6d8c` | workflow exists; verification still pending |

## Current pricing-source posture

- Source metadata policy is integrated and classifies pricing sources by deterministic metadata.
- Agreement gate is integrated and can classify pricing evidence.
- Yahoo/yfinance remains fallback/provisional evidence and must not be the sole route to valuation-grade UCITS pricing.
- Issuer NAV remains reference/stale-check evidence only and does not count as independent market-close agreement evidence.
- Stooq remains provisional / cross-check evidence until policy and provider coverage allow stronger use.
- Börse Frankfurt / Xetra remains exchange-candidate evidence while source/license review is unresolved.

## Current valuation-pricing posture

The agreement-aware wrapper exists:

```text
pricing/build_ucits_valuation_prices_with_agreement.py
```

It wraps the existing valuation builder and enriches output rows with `agreement_gate_evidence` while preserving conservative authority boundaries.

Current policy remains:

```text
valuation_grade=false unless source policy and agreement gate explicitly permit it
valuation_grade_row_count=0 in the current bootstrap posture
funding_authority=false
portfolio_mutation=false
production_delivery=false
```

## Current report-surface posture

The pricing-surface wrapper exists:

```text
runtime/render_etf_eu_report_with_pricing_surface.py
runtime/etf_eu_pricing_surface.py
tools/validate_etf_eu_pricing_surface.py
```

It can expose agreement-gate pricing evidence in the Dutch-first and English companion report surface, but the surface is not portfolio authority, not funding authority, not a buy recommendation and not delivery enablement.

## Current fundability posture

The fundability promotion contract exists:

```text
control/UCITS_FUNDABILITY_PROMOTION_CONTRACT_V1.md
tools/validate_ucits_fundability_promotion_contract.py
tests/test_ucits_fundability_promotion_contract.py
```

Current decision:

```text
no candidate is fundable
no candidate is funded
no automatic promotion from pricing success or report visibility is allowed
```

A future promotion decision must pass instrument identity, EU investability, trading-line, pricing-quality, tradability/liquidity, portfolio-role and explicit decision gates.

## Current workflow posture

The non-production pricing-surface shadow workflow exists:

```text
.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml
```

It is intended to run the agreement-aware wrapper, report pricing surface, pricing-surface validator and fundability validator without delivery.

Verification status:

```text
shadow_workflow_created=true
shadow_workflow_verification=pending
```

The latest run-queue commits did not yet produce connector-visible workflow-run evidence. Do not claim shadow workflow success until either GitHub Actions confirms success or a validation evidence artifact is committed under `output/validation/`.

## Pending items

- shadow workflow verification;
- main workflow wrapper switch;
- production Dutch-first report;
- delivery enablement.

## Standing authority boundaries

Until a future decision log entry and validator-backed implementation explicitly change them:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

## Current state files

Preferred EU state files:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
```

Temporary compatibility files may exist from the cloned U.S. runtime. They are not EU current-position truth unless explicitly re-authorized.

## Stable decision

The EU repo should not be a mechanical ticker replacement. It should be a separate UCITS investment-universe product using the proven runtime/reporting engine as scaffolding.

The current architecture decision is:

```text
typed pricing evidence spine
→ source metadata policy
→ agreement gate
→ agreement-aware valuation bridge
→ evidence-only report pricing surface
→ fundability contract
→ shadow workflow verification
→ main workflow switch only after verification
→ Dutch-first production report
→ delivery only after validators and receipt/manifest path exist
```
