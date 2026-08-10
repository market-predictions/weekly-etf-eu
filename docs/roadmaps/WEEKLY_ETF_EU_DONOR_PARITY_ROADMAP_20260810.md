# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date: 2026-08-10
Issue: #90
PR: #91
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`
Status: `IMPLEMENTATION_CONVERGED_PRE_ASSURANCE`

## Goal
Bring `weekly-etf-eu` to behavioral parity with the mature `weekly-etf` donor wherever product behavior should match, while preserving deliberate EU-specific UCITS/ISIN/KID/exact-trading-line requirements.

Governing rule: **port behavior, not U.S. assumptions**.

## Five-layer gap program

### 1. Decision framework — IMPLEMENTED
- Retired 50% maximum-position, 35% minimum-cash and 15% maximum-new-ETF shadow rules are non-executable.
- 75% is pricing-coverage context, not a position cap.
- 25% turnover and 18% semiconductor values remain research/shadow only unless explicitly adopted later.
- Embedded thematic exposure is measured lower-bound evidence, not a required minimum.
- Donor fresh-cash, replacement-duel, action-clock, cash-policy, contribution, hedge and factor-overlap behavior is represented in an EU-specific decision contract.
- Donor cash >3%/>5% and ~40% factor rules are review/disclosure triggers, not allocation caps.
- No maximum active-position rule is inherited accidentally from historical transition policy.

### 2. Input/state contract — IMPLEMENTED
- Model investability is broker-neutral; broker permission belongs only to the real execution boundary.
- Protected portfolio shares/cash plus current completed-close valuation remain live state authority.
- Recommendation memory is rebuilt for every funded position, including L0CK.
- Historical CAP01/transition target weights are isolated as non-current audit metadata before rendering.
- Missing current re-underwriting is explicitly `UNRESOLVED`, not an implicit Hold.
- Macro freshness is bound to donor source evidence date, not EU wrapper-generation date.
- UCITS registry is identity/investability authority only; mutable funded status comes from protected portfolio state.

### 3. Output contract — IMPLEMENTED
- Shadow policy values cannot appear as current controls.
- The post-normalization funded shadow renderer that recreated 7.50% reserve/strategic-target/three-position copy was removed.
- Current position count is dynamic and includes all four funded positions.
- Position tables show current weight and re-underwriting status, not historical phase targets.
- NL-primary and EN-companion output derive from one normalized state.
- Renderer fails closed on retired target/fixed-reserve/three-position copy and missing funded tickers.

### 4. Operational runbook — IMPLEMENTED
- Canonical lifecycle is candidate build → independent assurance → merge/exact-main → separately authorized guarded delivery.
- Candidate routine is non-main only and cannot push candidate output to main, self-assure or deliver.
- Completed-close resolution is dynamic rather than hard-coded to a repair date.
- Nineteen historical activation/send/repair/preview workflows are retained as `.yml.disabled` audit history and cannot execute.
- Controlled transport is the sole active real delivery route and validates an exact guarded-delivery authority record plus six artifact SHA-256 hashes.
- Controlled transport sends the approved artifacts and does not re-render them.

### 5. Governance/release assurance — IMPLEMENTED TO HANDOVER GATE
- One active release-integration claim: `ETF-EU-DONOR-PARITY-RECONCILIATION-V1`.
- Machine release evidence is explicitly preflight evidence only; it cannot issue independent assurance, merge authority or delivery authority.
- Exact-head implementation tests are required before handover.
- Independent `governance_release_assurance` must review a frozen exact PR #91 head.
- Merge only after PASS and unchanged head.
- Post-merge exact-main validation and lifecycle reconciliation remain mandatory.
- Delivery remains a separate later action requiring explicit guarded-send authority and positive receipt evidence.

## Execution waves

### Wave A — Authority repair — COMPLETE
Evidence:
- `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`
- historical transition/CAP01 configs marked non-executable;
- allocation/regression tests.

### Wave B — Donor-parity state and decision layer — COMPLETE
Evidence:
- `runtime/apply_etf_eu_donor_parity_contract.py`
- per-run scorecard contract;
- target-metadata sanitization;
- explicit unresolved re-underwriting semantics;
- donor discovery/fundability bridge.

### Wave C — Canonical routine convergence — COMPLETE
Evidence:
- `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`
- candidate-only routine workflow;
- exact-assured controlled transport;
- historical workflow disablement;
- dynamic completed-close and macro provenance.

### Wave D — Assurance and lifecycle closeout — IN PROGRESS
Definition of done:
- final exact-head CI green;
- implementation handover frozen;
- independent assurance `PASS`;
- PR #91 merged without head drift;
- exact-main validation green;
- issue #90 and integration claim closed;
- project and central Control state reconciled;
- no report delivery claimed from this repair line.

## Donor-parity matrix

| Donor behavior | ETF EU implementation | Status |
|---|---|---|
| State outranks markdown | protected portfolio/pricing/recommendation state outranks client copy | PARITY |
| Fresh-cash re-underwriting | per-funded-position current decision memory; missing evidence unresolved | PARITY |
| Thesis vs implementation | explicit separate fields | PARITY |
| Direct alternative duel | replacement close/duel memory | PARITY |
| Action clock | replaceability timer/escalation field | PARITY |
| Contribution/drag | numeric/qualitative contribution fields | PARITY |
| Factor overlap | overlap review + ~40% disclosure trigger, never position cap | PARITY |
| Hedge validity | explicit ballast/hedge validity review | PARITY |
| Cash policy | classification + >3% deploy-or-explain conditional + >5% material flag | PARITY |
| Broad discovery before runtime | donor-lane → UCITS bridge before fundability | PARITY WITH EU GATES |
| Challenger pricing is not automatic funding | explicit fundability + allocation-decision boundary | PARITY |
| Bilingual single-state rendering | NL/EN from one normalized EU state | PARITY |
| U.S. security identity | replaced by ISIN-first UCITS/KID/exact-line identity | INTENTIONAL EU DIVERGENCE |
| Donor operational legacy send/state-refresh routes | not copied; EU uses stricter candidate/assurance/delivery separation | INTENTIONAL EU HARDENING |

## Intentional EU divergences to preserve
- ISIN-first identity and exact share class/trading line.
- UCITS + PRIIPs/KID model-investability gates.
- U.S.-listed ETFs as research proxies only.
- EUR trading-line preference where practical.
- Dutch-primary client output.
- Broker-neutral model portfolio; broker permission only at real execution boundary.
- No real broker execution from report workflow.
- Stricter independent release/delivery role separation than legacy donor operations where donor weaknesses would otherwise be copied.

## Stop/escalation criteria
Escalate to the principal only for a genuine strategic choice that cannot be derived from donor behavior or existing EU authority, such as adopting a new portfolio concentration cap. Missing implementation details, stale administration and contradictory repo text are implementation/controller work, not principal blockers.
