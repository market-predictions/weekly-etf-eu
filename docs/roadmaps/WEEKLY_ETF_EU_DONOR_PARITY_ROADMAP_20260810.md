# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date: 2026-08-10
Parent issue: #90
Prior PR: #91 — MERGED
Post-merge repair issue: #94
Active repair PR: #95
Active branch: `agent/etf-eu-post-merge-us-donor-leak-repair-v1`
Status: `POST_MERGE_P0_DONOR_EXECUTION_LEAK_REPAIR_ACTIVE`

## Goal
Bring `weekly-etf-eu` to behavioral parity with the mature `weekly-etf` donor wherever product behavior should match, while preserving deliberate EU-specific UCITS/ISIN/KID/exact-trading-line requirements and preventing donor operational state from becoming ETF EU authority.

Governing rule: **port behavior, not U.S. assumptions or U.S. execution state**.

## Assurance and merge history

### PR #91 first assurance
Issue #92 reviewed frozen head `a9f93af018623011ac4b2cae742d69ea1441b4ca` and returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

Blockers were pricing-v2 contract incoherence and hard-coded three-position Markdown omitting L0CK.

### PR #91 repair re-assurance
Those blockers were repaired. Issue #93 independently reviewed frozen head:

`686c658c03d5ba4cbd208e254822a73b3fb514f2`

and returned:

`ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS`

PR #91 was merged unchanged as:

`202b0a629af34c697c7b7cb8fdce97fbb56bddbc`

That PASS remains valid for the candidate it reviewed; it does not cover later post-merge bot output.

## Five-layer status

### 1. Decision framework — COMPLETE / NOT REOPENED
- retired 50% maximum position, 35% minimum cash and 15% maximum new ETF remain non-executable;
- 75% remains pricing coverage, not a position cap;
- 25% turnover and 18% semiconductor/theme values remain research/shadow only;
- donor cash >3%/>5% and ~40% factor thresholds remain review/disclosure triggers, not allocation caps;
- fresh-cash, replacement-duel, action-clock, contribution, hedge and factor-overlap concepts remain represented.

### 2. Input/state contract — COMPLETE FOR CANONICAL EU PATH
Canonical pricing path remains:

```text
candidate request report_date
→ provider qualification on exact report_date
→ ucits_close_price_validation_basket_results_v2
→ funded two-provider same-date consensus
→ shared v2 validator
→ v2 normalized state
→ candidate package
```

The protected funded state remains VWCE/EUNA/SXR8/L0CK. Historical donor `output/etf_portfolio_state.json` is not ETF EU state authority.

### 3. Output contract — COMPLETE FOR CANONICAL EU PATH
NL/EN Markdown/HTML/PDF are state-derived and dynamic for the four protected funded positions. Three-position, retired-target, fixed-reserve and internal-enum leakage fail closed.

Legacy donor `weekly_analysis_pro_*` and `send_report.py` surfaces are not ETF EU client-output authority.

### 4. Operational runbook — POST-MERGE P0 REPAIR ACTIVE
The intended canonical lifecycle remains:

`candidate → independent assurance → merge/exact-main → separately authorized guarded delivery`

PR #91 post-merge validation exposed that two older donor workflows were still active outside that canonical path:
- `persist-etf-pricing-audit.yml`;
- `validate-etf-runtime.yml`.

Both invoked retained US Weekly ETF runtime `pricing.run_pricing_pass`; the second also invoked legacy `send_report.py` rendering. The pricing-audit workflow wrote US pricing artifacts to ETF EU `main`.

PR #95 now retires both to `.yml.disabled`, removes the leaked artifacts and prevents any active workflow from invoking donor-only pricing/report execution surfaces.

### 5. Governance/release assurance — NEW SUCCESSOR CYCLE REQUIRED
- issue #93 PASS and PR #91 merge are historical valid evidence;
- bot commit `d771bde734ffda6120a77b1f4fe0e99bd198cc96` is the post-merge defect trigger, not approved semantic release evidence;
- old claim `ETF-EU-DONOR-PARITY-RECONCILIATION-V1` is `SUPERSEDED`;
- successor claim `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1` owns issue #94 / PR #95;
- PR #95 requires its own exact-head CI and independent assurance before merge;
- issue #90 remains open until successor exact-main closeout.

## Execution waves

### Wave A — Allocation/authority repair — COMPLETE
### Wave B — Donor-parity state/decision layer — COMPLETE
### Wave C — Canonical EU candidate/delivery topology — COMPLETE
### Wave D1 — PR #91 assurance-fail pricing/Markdown repair — COMPLETE
### Wave D2 — PR #91 fresh assurance and merge — COMPLETE

Evidence:
- issue #93 = PASS on `686c658c...`;
- merge commit = `202b0a629...`.

### Wave D3 — Post-merge donor execution leak repair — ACTIVE

Trigger:
- bot commit `d771bde734ffda6120a77b1f4fe0e99bd198cc96` added US Weekly ETF pricing audit/cache after PR #91 merge.

Repair work package:
- `control/work_packages/ETF_EU_POST_MERGE_US_DONOR_LEAK_REPAIR_V1_20260810.md`

Definition of implementation convergence:
1. two donor execution workflows disabled and retained only as audit history;
2. two leaked US artifacts absent from PR #95 candidate;
3. product-boundary gate rejects active donor pricing/report tokens;
4. workflow-authority gate rejects active donor pricing/report tokens and requires disabled evidence;
5. planted tests pass;
6. no additional active donor execution routes remain;
7. protected EU state/ledger unchanged;
8. roadmap/current state/claim/changelog/handover reconciled.

### Wave D4 — Fresh assurance and final lifecycle closeout — NEXT
Definition of done:
1. PR #95 exact-head CI green;
2. exact head frozen;
3. independent `ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS` on that head;
4. reviewed head unchanged;
5. PR #95 merged;
6. exact-main product/workflow authority green;
7. no US donor pricing artifact regenerated on `main`;
8. issue #94 and parent issue #90 closed;
9. successor claim `CLOSED` with closeout handover;
10. project and central Control state reconciled;
11. no report delivery claimed from this repair line.

## Donor-parity matrix

| Donor behavior | ETF EU implementation | Status |
|---|---|---|
| State outranks Markdown | protected/current normalized state governs MD/HTML/PDF | PARITY |
| Fresh-cash re-underwriting | current per-funded-position memory; missing evidence unresolved | PARITY |
| Thesis vs implementation | explicit separate fields | PARITY |
| Direct alternative duel | replacement close/duel memory | PARITY |
| Action clock | replaceability timer/escalation | PARITY |
| Contribution/drag | current contribution fields | PARITY |
| Factor overlap | ~40% disclosure trigger, not cap | PARITY |
| Hedge validity | explicit ballast/hedge validity review | PARITY |
| Cash policy | >3% deploy-or-explain conditional; >5% material disclosure | PARITY |
| Broad discovery before runtime | donor-lane → UCITS bridge before fundability | PARITY WITH EU GATES |
| Pricing evidence boundary | exact report-date funded two-provider consensus under one v2 contract | PARITY |
| Challenger pricing is not funding | fundability + explicit allocation boundary | PARITY |
| Bilingual single-state output | NL/EN MD/HTML/PDF from one normalized state | PARITY |
| U.S. security identity | ISIN-first UCITS/KID/exact-line identity | INTENTIONAL EU DIVERGENCE |
| US donor operational runtime | retained only as historical code; never active ETF EU workflow authority | INTENTIONAL EU HARDENING / PR95 |
| Legacy send/activation routes | stricter candidate/assurance/delivery separation | INTENTIONAL EU HARDENING |

## Intentional EU divergences to preserve
- ISIN-first identity and exact share class/trading line;
- UCITS + PRIIPs/KID model-investability gates;
- U.S.-listed ETFs as research proxies only;
- EUR trading-line preference where practical;
- Dutch-primary client output;
- broker-neutral model portfolio;
- no real broker execution from report workflow;
- stricter independent release/delivery role separation;
- no active US Weekly ETF donor pricing/report runtime.

## Stop/escalation criteria
Escalate to the principal only for a genuine strategic choice that cannot be derived from donor behavior or existing EU authority. The post-merge donor leak is an implementation/product-boundary defect and requires no principal decision.
