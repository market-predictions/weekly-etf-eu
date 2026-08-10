# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date: 2026-08-10
Parent issue: #90
Prior PR: #91 — MERGED
Post-merge repair issue: #94
Active repair PR: #95
Branch: `agent/etf-eu-post-merge-us-donor-leak-repair-v1`
Status: `POST_MERGE_REPAIR_HANDOVER_READY_FRESH_ASSURANCE_REQUIRED`

## Goal
Bring `weekly-etf-eu` to behavioral parity with mature `weekly-etf` where behavior should match, while preserving EU-specific UCITS/ISIN/KID/exact-line controls and preventing US donor operational state from becoming ETF EU authority.

Governing rule: **port behavior, not U.S. assumptions, filenames, state or execution routes**.

## Completed waves

### Wave A — Allocation/authority repair — COMPLETE
- 50% maximum position, 35% minimum cash, 15% maximum new ETF retired;
- 75% is pricing coverage only;
- 25% turnover and 18% semiconductor/theme values research-only;
- donor >3%/>5% cash and ~40% factor thresholds review/disclosure triggers only.

### Wave B — Donor-parity state/decision layer — COMPLETE
- protected funded state VWCE/EUNA/SXR8/L0CK;
- current fresh-cash/re-underwriting memory;
- thesis/implementation, replacement duel, action clock, contribution, factor overlap, hedge validity and cash classification;
- missing current evidence remains unresolved rather than implicit Hold.

### Wave C — Canonical EU candidate/output/delivery topology — COMPLETE
- EU/UCITS v2 pricing contract;
- report-date-bound funded two-provider consensus;
- one normalized state for NL/EN MD/HTML/PDF;
- dynamic four-position output including L0CK;
- candidate-only non-main build;
- independent assurance separated from implementation;
- one guarded real delivery route;
- historical activation/send/repair/shadow routes non-executable.

### Wave D1 — PR #91 assurance FAIL repair — COMPLETE
Issue #92 correctly found pricing-v2 and Markdown defects. They were repaired and package-level regression coverage added.

### Wave D2 — PR #91 independent re-assurance and merge — COMPLETE
- issue #93 verdict: PASS;
- reviewed head: `686c658c03d5ba4cbd208e254822a73b3fb514f2`;
- merge: `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`.

### Wave D3 — Post-merge US donor execution leak repair — IMPLEMENTATION COMPLETE
Post-merge bot commit `d771bde734ffda6120a77b1f4fe0e99bd198cc96` proved three legacy donor/report routes still sat in the active ETF EU workflow topology.

Retired in PR #95:
1. `persist-etf-pricing-audit.yml` — wrote US donor pricing artifacts to main;
2. `validate-etf-runtime.yml` — ran donor pricing plus legacy `send_report.py`;
3. `validate-etf-lane-breadth.yml` — validated donor `weekly_analysis_pro_*` report files.

Their audit copies remain as `.yml.disabled`. The two leaked US pricing artifacts are deleted in the repaired candidate.

Preventive gates now reject active donor execution/report tokens across all `.yml/.yaml` workflows.

Semantic baseline:

`d9b5731bbd0b125e2df9b778282116f9d8c32314`

Evidence:
- product boundary `31436751783`: SUCCESS;
- donor parity/full-package `31436751773`: SUCCESS;
- 31 package/blocker regressions passed;
- topology: `32 active | 23 retired-disabled | candidate=1 | delivery=1 | US donor execution=0`.

## Next wave

### Wave D4 — Fresh PR #95 assurance and final closeout — PENDING INDEPENDENT ROLE-B
1. freeze exact live PR #95 head after atomic handover commit;
2. independent `ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS | FAIL | INDETERMINATE`;
3. merge only on PASS + unchanged head;
4. exact-main product/workflow boundary validation;
5. prove no US donor pricing artifact regenerates;
6. verify protected EU state/ledger unchanged;
7. close issue #94, parent issue #90 and successor claim;
8. reconcile central Control state.

## Parity matrix

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
| US donor operational runtime | not executable in ETF EU | INTENTIONAL EU HARDENING |
| Real delivery | separately guarded exact-artifact transport | INTENTIONAL EU HARDENING |

## Decisions not reopened
The post-merge incident is an operational/product-boundary defect. It creates no new allocation decision, position cap, cash floor or execution authority.

## Stop/escalation criteria
No principal decision is required for this repair. The only remaining gate is independent assurance of the frozen PR #95 candidate. Delivery and broker execution remain outside this roadmap wave.
