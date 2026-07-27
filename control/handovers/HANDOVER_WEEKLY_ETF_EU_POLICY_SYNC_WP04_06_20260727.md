# Handover — Weekly ETF EU Policy Synchronization Shadow

Date: 2026-07-27  
Repository: `market-predictions/weekly-etf-eu`  
Branch: `sync/donor-report-parity`  
Draft PR: #66  
Status: presentable technical shadow; not merged, activated, delivered or executed

> This document records a simulated model-portfolio test. It is not investment advice, an order instruction or authorization to change any portfolio.

## Completed scope

The branch now provides:

- consumption of the Weekly ETF donor strategy state and exposure-level target;
- exact UCITS mapping with machine-readable blockers;
- completed-close and traded-value connectivity evidence;
- an incumbent overlap and disposition review;
- a policy-constrained Stage-1 simulation;
- a non-optimizing fixed-composition risk replay;
- a reconciled bilingual sister report using the donor section, table and visual contract.

The official EU model portfolio and all delivery state remain unchanged.

## Reference portfolio

```text
VWCE: 151 shares, 24.866766%
EUNA: 1,526 shares, 7.483242%
SXR8: 10 shares, 7.063180%
cash: approximately 60.59%
NAV: EUR 99,756.76
```

## Policy-constrained Stage-1 simulation

The original fixed-50 prototype has been superseded by `staged_policy_driven_v1`.

Controls:

```text
maximum positions: 8
maximum simulated gross turnover: 25.00% NAV
minimum simulated post-stage cash: 35.00% NAV
maximum new direct ETF weight: 15.00% NAV
minimum new simulated allocation: 2.00% NAV
minimum 20-day median traded value: EUR 500,000
maximum evidence age: 7 calendar days
whole-share simulation only: true
incumbent reductions in Stage 1: false
effective semiconductor cap: 18.00% NAV
effective cybersecurity cap: 15.00% NAV
```

Simulated Stage-1 quantities:

```text
VVSM: 156 shares, 14.804530% direct weight
LOCK: 995 shares, 10.187711% direct weight
VWCE: retained at 151 shares
EUNA: retained at 1,526 shares
SXR8: retained at 10 shares
```

Simulated outcome:

```text
position count: 5
gross allocation value: EUR 24,931.45
gross turnover: 24.992241% NAV
estimated friction: EUR 24.93
projected invested value: EUR 64,248.77
projected cash: EUR 35,483.06
projected cash weight: 35.569579%
incumbent reductions: none
```

These quantities exist only inside non-authoritative shadow artifacts.

## Incumbent overlap findings

The overlap method is a lower-bound calculation based on documented issuer holdings. It does not claim complete constituent coverage.

```text
VWCE versus SXR8 documented overlap lower bound: 20.947990 percentage points
VWCE versus VVSM documented overlap lower bound: 9.111860 percentage points
SXR8 versus VVSM documented overlap lower bound: 11.870000 percentage points
```

Documented semiconductor exposure already embedded in the current portfolio:

```text
VWCE contribution: 2.265825% NAV
SXR8 contribution: 0.838399% NAV
total incumbent lower bound: 3.104224% NAV
```

The simulated VVSM sleeve plus documented incumbent exposure reaches 17.908754% NAV, below the 18.00% policy cap.

Disposition used by the simulation:

- `VWCE`: retain as a global-core candidate; determine a permanent cap after remaining mappings are complete.
- `SXR8`: retain in Stage 1; prioritize for a later overlap review once an ex-US core is eligible.
- `EUNA`: retain until a separate volatility, drawdown and risk-budget review assesses its stabilizing role.

A measured zero cybersecurity overlap is not interpreted as zero actual overlap because the documented LOCK holdings set is incomplete.

## Remaining implementation blockers

- `IXUA`: identity, line, price and liquidity pass; KID verification remains incomplete.
- `PCOM`: traded value is below policy and its swap structure requires additional review.
- Grid, biotech, healthcare, uranium and utilities mappings remain unresolved.
- Defense and agriculture are promoted research opportunities but are not current donor target sleeves; their EU mappings also remain unresolved.

## Fixed-composition risk replay

The simulation was replayed over one common EUR price window:

```text
window: 2025-07-24 through 2026-07-24
return observations: 251
historical decisions reconstructed: false
optimization performed: false
purpose: risk sanity check only
```

| Composition | Annualized return | Annualized volatility | Maximum drawdown |
|---|---:|---:|---:|
| Current EU composition | 7.07% | 3.81% | -2.18% |
| Strict mapped composition | 32.69% | 12.37% | -4.91% |
| Fixed-50 composition | 23.35% | 9.58% | -3.58% |
| Policy-driven composition | 24.98% | 10.16% | -3.82% |

This is not a strategy backtest or expected-return estimate. It only shows how today’s fixed compositions would have behaved over the common historical window.

## Final report state

The Dutch and English reports each contain 11 substantive pages with matching pagination.

The report distinguishes:

1. donor strategic target;
2. EU implementation status;
3. feasible Stage-1 simulation;
4. current official EU weight;
5. simulated transition intent;
6. authority and activation boundary.

Reconciled simulated weights:

```text
VVSM: current 0.00%, Stage-1 simulation 14.80%
LOCK: current 0.00%, Stage-1 simulation 10.19%
cash: current 60.59%, Stage-1 simulation 35.57%
VWCE: unchanged at 24.87%
EUNA: unchanged at 7.48%
SXR8: unchanged at 7.06%
```

Section 14 contains only the two actionable simulation rows. Deferred exposures remain documented in Sections 11 and 13. Sections 15 and 16 form a deliberate operational appendix page.

## Validation evidence

### Transition replay

```text
workflow: Validate ETF EU transition composition replay
run_id: 30311016298
conclusion: success
artifact_id: 8670353877
```

### Reconciled allocator report

```text
workflow: Validate ETF EU allocator report shadow
run_id: 30312745857
conclusion: success
head_sha: 30ee52fb9a3f005c18fc66ab5c743fc532b8bdba
artifact_id: 8671029503
artifact_digest: sha256:a6b4d89116f504ff223d8779198c02344cd7d2a2b79250ef03fd1bee6fde987f
```

All report gates passed: allocator surface, overlap surface, reconciliation, intent compaction, pagination, PDF integrity, bilingual parity, client-language checks and donor surface parity.

Visual review passed for all 11 pages in both languages: no clipping, blank pages, broken glyphs or split decision rows.

## Hard production boundary

This milestone does not authorize:

- merging either draft PR;
- changing the official EU model portfolio;
- creating ledger entries;
- treating connectivity evidence as valuation-grade;
- placing orders;
- sending the synchronized report;
- starting Stage 2.

## Next safe work package — WP-SYNC-07 cutover readiness

Before controlled promotion:

1. review and merge the versioned donor contract;
2. replace the cross-branch dependency with a merged contract version;
3. obtain fresh accepted valuation evidence and spread/tradability evidence;
4. make an explicit EUNA risk-budget decision;
5. resolve the IXUA KID and prioritized missing mappings;
6. define Stage-2 entry, source and rollback rules;
7. test Gmail MIME/CID delivery and verify the received message;
8. prepare a separate activation package;
9. require explicit user authorization before any official model-portfolio mutation.

## Decision boundary

The result is suitable for architecture, methodology, risk and report review. It is not an activation package.
