# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date opened: 2026-08-10
Date closed: 2026-08-11
Parent issue: #90
PR #91: merged
Post-merge repair issue: #94
PR #95: merged
Status: `COMPLETE`

## Goal
Bring `weekly-etf-eu` to behavioral parity with mature `weekly-etf` where behavior should match, while preserving EU-specific UCITS/ISIN/KID/exact-line controls and preventing U.S. donor operational state from becoming ETF EU authority.

Governing rule: **port behavior, not U.S. assumptions, filenames, state or execution routes**.

## Final outcome

### Wave A — Allocation/authority repair — COMPLETE
- 50% maximum position, 35% minimum cash and 15% maximum new ETF retired as current authority;
- 75% is pricing coverage only;
- 25% turnover and 18% semiconductor/theme values remain research/shadow only;
- donor cash/factor thresholds remain review/disclosure triggers rather than allocation caps.

### Wave B — Donor-parity state/decision layer — COMPLETE
- protected funded state VWCE/EUNA/SXR8/L0CK;
- current fresh-cash/re-underwriting memory;
- thesis/implementation, replacement duel, action clock, contribution, factor overlap, hedge validity and cash classification;
- missing current evidence remains unresolved rather than implicit Hold.

### Wave C — Canonical EU candidate/output/delivery topology — COMPLETE
- one coherent EU/UCITS v2 pricing contract;
- exact report-date funded two-provider consensus;
- one normalized state for NL/EN MD/HTML/PDF;
- dynamic four-position output including L0CK;
- candidate-only non-main build;
- independent assurance separated from implementation;
- one separately guarded real delivery route;
- historical activation/send/repair/shadow routes non-executable.

### Wave D1 — PR #91 assurance FAIL repair — COMPLETE
Issue #92 found two real implementation defects: pricing-contract incoherence and stale Markdown/L0CK output. Both were repaired and full package-level regression coverage was added.

### Wave D2 — PR #91 re-assurance and merge — COMPLETE
- issue #93: PASS;
- reviewed head: `686c658c03d5ba4cbd208e254822a73b3fb514f2`;
- merge: `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`.

### Wave D3 — Post-merge US donor execution leak repair — COMPLETE
Exact-main observation after PR #91 exposed three still-active U.S. donor operational/report paths. Issue #94 / PR #95:
- retired `persist-etf-pricing-audit.yml`;
- retired `validate-etf-runtime.yml`;
- retired `validate-etf-lane-breadth.yml`;
- removed two leaked U.S. pricing artifacts;
- hardened product-boundary and workflow-authority gates against active donor execution/report tokens.

### Wave D4 — Fresh PR #95 assurance and final closeout — COMPLETE
Independent issue #96 returned:

`ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS`

Reviewed head:

`e5d3470e1e1ab7f402a02cb31b775f3f902d4928`

PR #95 merged unchanged as:

`10823b7c457a253e409a768f52ee95b1522c363f`

Exact-main push run `31472717495` returned product-boundary PASS with 6 planted tests, 32 active workflows scanned and no blockers. The real merge tree equals the assurance synthetic merge tree:

`71a614575bdc1d675ece53684d14601ce76fde90`

Thus the workflow-authority evidence applies to exact merged code content:

```text
active_workflows=32
retired_disabled=23
candidate_route=1
delivery_route=1
us_donor_execution_routes=0
```

No retired donor workflow re-executed and no erroneous U.S. pricing artifact regenerated.

## Final parity matrix

| Donor behavior | ETF EU implementation | Status |
|---|---|---|
| State outranks Markdown | protected/current normalized state governs all client surfaces | PARITY |
| Fresh-cash re-underwriting | current per-funded-position memory | PARITY |
| Thesis vs implementation | separate fields | PARITY |
| Replacement duel/action clock | current decision memory | PARITY |
| Contribution/factor/hedge review | explicit current fields | PARITY |
| Cash policy | deploy-or-explain/material disclosure triggers only | PARITY |
| Broad discovery | donor behavior bridged into EU UCITS mapping/fundability | PARITY WITH EU GATES |
| Pricing evidence | exact report date + funded two-provider consensus | PARITY WITH EU GATES |
| Bilingual output | NL/EN MD/HTML/PDF from one state | PARITY |
| Identity | ISIN-first UCITS/KID/exact-line | INTENTIONAL EU DIVERGENCE |
| U.S. donor operational runtime | non-executable in ETF EU | INTENTIONAL EU HARDENING |
| Real delivery | separately guarded exact-artifact transport | INTENTIONAL EU HARDENING |

## Protected portfolio at closeout

```text
VWCE=151
EUNA=1526
SXR8=10
L0CK=934
cash_eur=50208.40
portfolio_blob=df710b5fbe4172506b67b7f591030a8c6a098c64
trade_ledger_blob=c6765ba380fe0c40272688a017dc0dc99b46d571
```

No allocation decision was reopened by the post-merge repair.

## Lifecycle closeout

Successor claim `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1` is CLOSED.

Closeout handover:

`handover/ETF_EU_POST_MERGE_US_DONOR_LEAK_REPAIR_V1_CLOSE_20260811.md`

Parent issue #90 and repair issue #94 may close after this repository-backed closeout record and corresponding issue closeout comments are present.

## Next roadmap boundary

The next genuinely current Weekly ETF EU report is a separate production cycle, not an extension of this reconciliation roadmap. It requires a new candidate/work claim, current completed-close pricing, current re-underwriting, fresh independent assurance and separate guarded delivery authority.
