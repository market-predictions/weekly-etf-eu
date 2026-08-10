# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date: 2026-08-10
Issue: #90
PR: #91
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`
Status: `ASSURANCE_FAIL_REPAIR_ACTIVE`

## Goal
Bring `weekly-etf-eu` to behavioral parity with the mature `weekly-etf` donor wherever product behavior should match, while preserving deliberate EU-specific UCITS/ISIN/KID/exact-trading-line requirements.

Governing rule: **port behavior, not U.S. assumptions**.

## Current release state

Independent assurance issue #92 reviewed frozen head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

and returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

The failed candidate is historical evidence only. PR #91 is back in draft implementation state. Merge and delivery are blocked until a new semantic head passes a fresh independent assurance cycle.

The reviewer confirmed the existing donor-parity authority decisions and found two implementation/output-contract gaps:
1. canonical pricing builder → validator → normalized-state contract was not coherently v2 and did not fail closed on the report-date/funded-consensus boundary;
2. NL/EN Markdown delivery artifacts still contained a hard-coded three-position surface and omitted L0CK.

Repair package:

`control/work_packages/ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_V1_20260810.md`

## Five-layer gap program

### 1. Decision framework — COMPLETE / NOT REOPENED
- 50% maximum-position, 35% minimum-cash and 15% maximum-new-ETF shadow rules are retired and non-executable.
- 75% is pricing-coverage context, not a position cap.
- 25% turnover and 18% semiconductor values remain research/shadow only unless explicitly adopted later.
- Embedded thematic exposure is measured lower-bound evidence, not a required minimum.
- Donor fresh-cash, replacement-duel, action-clock, cash-policy, contribution, hedge and factor-overlap behavior is represented in the EU decision contract.
- Donor cash >3%/>5% and ~40% factor thresholds are review/disclosure triggers, not allocation caps.

### 2. Input/state contract — REPAIRING PRICING EXECUTION BOUNDARY
Already retained:
- broker-neutral model investability;
- protected portfolio + ledger authority;
- recommendation memory for every funded position including L0CK;
- historical CAP01 targets non-current;
- missing re-underwriting explicitly `UNRESOLVED`;
- macro freshness from donor provenance;
- UCITS registry identity-only.

Repair now required/implemented on the active branch:

```text
candidate report_date
→ provider qualification on exact report_date
→ ucits_close_price_validation_basket_results_v2
→ funded two-provider consensus
→ shared v2 validator
→ v2 normalized state
```

Negative cases must fail: v1 schema, report-date drift, missing funded line, one-provider funded evidence and failed funded consensus.

### 3. Output contract — REPAIRING MARKDOWN DELIVERY SURFACE
HTML/PDF funded renderer remains dynamic and state-derived.

The missing parity layer is NL/EN Markdown, which is also a delivery artifact/plaintext email body. Current repair makes Markdown:
- dynamic on funded count;
- dynamic on funded ticker set including L0CK;
- state-derived rather than VWCE/EUNA/SXR8 hard-coded;
- fail-closed on three-position wording;
- fail-closed on retired strategic/phase targets and fixed 7.50% reserve wording;
- independently machine-validated in the candidate gate.

### 4. Operational runbook — COMPLETE EXCEPT REPAIRED CANDIDATE PROOF
- lifecycle remains candidate → independent assurance → merge/exact-main → separately authorized guarded delivery;
- candidate route is non-main and cannot self-assure/merge/deliver;
- 20 historical/parallel workflows remain disabled;
- three donor-shadow workflows remain research-only;
- controlled transport remains the sole real delivery route;
- candidate workflow now binds pricing generation and validation explicitly to `ETF_EU_REPORT_DATE` and requires funded consensus;
- Markdown validation is part of candidate machine evidence.

### 5. Governance/release assurance — FAILED ON OLD HEAD, NEW CYCLE REQUIRED
- issue #92 = historical FAIL record for `a9f93af...`;
- existing integration claim is reopened `ACTIVE`;
- repair work package is active;
- a new handover and a new assurance issue are mandatory after the repaired head is green;
- issue #92 may not be reused as assurance for a new semantic head.

## Execution waves

### Wave A — Authority repair — COMPLETE
Evidence:
- `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`;
- historical transition/CAP01 configs non-executable;
- authority regressions.

### Wave B — Donor-parity state and decision layer — COMPLETE
Evidence:
- `runtime/apply_etf_eu_donor_parity_contract.py`;
- per-run scorecard;
- target-metadata sanitization;
- unresolved re-underwriting semantics;
- donor discovery/fundability bridge.

### Wave C — Canonical routine convergence — COMPLETE
Evidence:
- `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`;
- candidate-only routine;
- controlled transport separation;
- 20 historical/parallel routes disabled;
- sister-report route retired;
- donor pin reduced to three research-only consumers;
- dynamic completed-close and macro provenance.

### Wave D1 — Assurance-fail implementation repair — IN PROGRESS
Definition of done:
- shared v2 pricing contract implemented and negative-tested;
- candidate workflow explicitly binds report date and funded consensus;
- normalized state consumes the same v2 contract;
- Markdown is fully state-derived and separately validated;
- executable end-to-end candidate pricing/state/Markdown regression passes;
- all normal PR gates pass on the final semantic head.

### Wave D2 — Fresh assurance and lifecycle closeout — PENDING D1
Definition of done:
- final repair implementation handover is the last candidate mutation;
- new exact PR #91 head frozen;
- fresh assurance issue returns PASS;
- reviewed head remains unchanged;
- PR #91 merged;
- exact-main validation green;
- issue #90 and integration claim closed;
- project and central Control state reconciled;
- no report delivery claimed from this repair line.

## Donor-parity matrix

| Donor behavior | ETF EU target state | Status |
|---|---|---|
| State outranks markdown | protected portfolio/pricing/recommendation state also governs MD delivery artifacts | REPAIRING → TARGET PARITY |
| Fresh-cash re-underwriting | per-funded-position current decision memory; missing evidence unresolved | PARITY |
| Thesis vs implementation | explicit separate fields | PARITY |
| Direct alternative duel | replacement close/duel memory | PARITY |
| Action clock | replaceability timer/escalation field | PARITY |
| Contribution/drag | numeric/qualitative contribution fields | PARITY |
| Factor overlap | ~40% disclosure trigger, never position cap | PARITY |
| Hedge validity | explicit ballast/hedge validity review | PARITY |
| Cash policy | >3% deploy-or-explain conditional + >5% material disclosure | PARITY |
| Broad discovery before runtime | donor-lane → UCITS bridge before fundability | PARITY WITH EU GATES |
| Pricing evidence boundary | funded two-provider completed-close consensus bound to candidate report date | REPAIRING → TARGET PARITY |
| Challenger pricing is not funding | explicit fundability + allocation-decision boundary | PARITY |
| Bilingual single-state rendering | NL/EN MD/HTML/PDF from one normalized state | REPAIRING MARKDOWN |
| U.S. security identity | ISIN-first UCITS/KID/exact-line identity | INTENTIONAL EU DIVERGENCE |
| Legacy operational send/state routes | stricter candidate/assurance/delivery separation | INTENTIONAL EU HARDENING |

## Intentional EU divergences to preserve
- ISIN-first identity and exact share class/trading line;
- UCITS + PRIIPs/KID model-investability gates;
- U.S.-listed ETFs as research proxies only;
- EUR trading-line preference where practical;
- Dutch-primary client output;
- broker-neutral model portfolio;
- no real broker execution from report workflow;
- stricter independent release/delivery role separation.

## Stop/escalation criteria
Escalate to the principal only for a genuine strategic choice that cannot be derived from donor behavior or existing EU authority. The current assurance FAIL requires implementation repair only; no principal decision is required.
