# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date: 2026-08-10
Issue: #90
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`

## Goal
Bring `weekly-etf-eu` to behavioral parity with the mature `weekly-etf` donor wherever product behavior should match, while preserving deliberate EU-specific UCITS/ISIN/KID/exact-trading-line requirements.

Governing rule: **port behavior, not U.S. assumptions**.

## Five-layer gap program

### 1. Decision framework — P0/P1
- Remove executable dependence on retired 35% minimum-cash and 15% maximum-new-ETF shadow rules.
- Treat 25% turnover and 18% semiconductor values as non-authoritative until explicitly adopted by a durable decision.
- Treat embedded semiconductor exposure as a measured lower bound, not a required minimum.
- Port donor fresh-cash re-underwriting, replacement-duel, action-clock, cash-policy and factor-overlap behavior into an EU-specific decision contract.
- Preserve a separately governed position-count rule only if explicitly adopted; do not inherit it accidentally from transition policy.

### 2. Input/state contract — P0/P1
- Resolve broker-neutrality contradiction: model investability requires UCITS/KID/identity/pricing, not broker account permission; real execution may require broker permission.
- Make protected portfolio shares/cash and current completed-close valuation the live state authority.
- Refresh recommendation memory for every funded position, including L0CK.
- Separate historical strategy targets from current executable allocation authority.
- Bind macro freshness to source evidence date, not wrapper-generation date.

### 3. Output contract — P0/P1
- Remove current-control presentation of shadow policy values.
- Remove fixed `Cash-first 50%` scenario from authoritative client surfaces.
- Label embedded overlap as `measured lower-bound exposure`.
- Preserve NL-primary / EN-companion parity from one normalized state.
- Prevent stale position counts, duplicate ticker rows and shadow-policy leakage by deterministic tests.

### 4. Operational runbook — P1
- Establish one canonical routine path: discovery → UCITS mapping → exact-line pricing → fundability → normalized state → bilingual render → validation → independent assurance → guarded delivery.
- Make report date resolve to the latest valid completed close rather than a hard-coded repair date.
- Classify legacy/repair workflows as canonical, diagnostic, migration-only or retired; stop using parallel release-authoritative paths.
- Preserve two-provider funded pricing and exact-line identity gates.

### 5. Governance/release assurance — P0/P1/P2
- One active release-integration claim.
- Exact-head implementation tests before PR review.
- Independent `governance_release_assurance` on frozen candidate.
- Merge only after PASS.
- Post-merge exact-main validation.
- Explicit handover disposition and claim closure.
- Delivery remains separate and requires transport + independent receipt/attachment evidence.

## Execution waves

### Wave A — Authority repair (P0)
Definition of done:
- retired 35/15 rules cannot affect allocation or client output;
- 25/18 remain research/shadow only unless separately adopted;
- embedded 3.10-style value is never represented as a control/minimum;
- broker-neutrality is internally consistent;
- tests fail on regression.

### Wave B — Donor-parity state and decision layer (P1)
Definition of done:
- EU recommendation scorecard contract covers all funded holdings;
- fresh-cash, replacement, action-clock, cash and overlap disciplines are represented in normalized EU state;
- discovery breadth is donor-like but fundability remains UCITS-gated;
- donor opportunity → UCITS line → pricing → fundability lineage is explicit.

### Wave C — Canonical routine convergence (P1)
Definition of done:
- one declared production path;
- completed-close date resolution is dynamic;
- non-canonical repair/migration workflows cannot silently become release authority;
- macro provenance and bilingual renderer lineage are explicit.

### Wave D — Assurance and lifecycle closeout (P2)
Definition of done:
- exact-head CI green;
- independent assurance PASS;
- merge and exact-main validation green;
- roadmap/current-state/next-actions/work-claims reconciled;
- handover `CLOSE` recorded;
- no report delivery claimed from this package.

## Intentional EU divergences to preserve
- ISIN-first identity and exact share class/trading line.
- UCITS + PRIIPs/KID model-investability gates.
- U.S.-listed ETFs as research proxies only.
- EUR trading-line preference where practical.
- Dutch-primary client output.
- Broker-neutral model portfolio; broker permission only at real execution boundary.
- No real broker execution from report workflow.

## Stop/escalation criteria
Escalate to the principal only for a genuine strategic choice that cannot be derived from donor behavior or existing EU authority, such as adopting a new portfolio concentration cap. Missing implementation details, stale administration and contradictory repo text are implementation/controller work, not principal blockers.
