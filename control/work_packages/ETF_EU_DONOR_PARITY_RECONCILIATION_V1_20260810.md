# ETF EU Donor-Parity Reconciliation V1

Work package: `ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1`
Issue: #90
Owner role: `implementation_operations`
Target: `main`
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`

## Problem statement
The EU product has strong UCITS/pricing/governance foundations but still contains transition-era authority and maturity gaps relative to the mature Weekly ETF donor. Some shadow-only values can leak into allocator/report semantics, the runbook contradicts broker-neutrality, recommendation memory is stale, and discovery/state/runbook convergence is incomplete.

## Scope
1. Authority repair.
2. Donor-parity decision/state contract.
3. Client-output semantics.
4. Canonical runbook convergence.
5. Tests, independent assurance and lifecycle closeout.

## Protected boundaries
- no portfolio state mutation;
- no trade-ledger write;
- no real broker execution;
- no report delivery or SMTP action;
- no weakening of UCITS/KID/ISIN/exact-line/two-provider funded pricing controls.

## Acceptance criteria
### Authority
- 35% minimum cash and 15% max new ETF are non-executable historical/shadow data.
- 25% turnover and 18% semiconductor cap have no current decision authority unless a separate decision adopts them.
- embedded semiconductor lower-bound exposure is not labelled or consumed as a minimum/control.
- `Cash-first 50%` is internal scenario material only.

### Broker-neutrality
- model investability does not require account-level broker permission;
- real execution may require broker permission;
- runbook and validators agree.

### Donor-parity decision/state
- every funded holding appears in recommendation memory;
- normalized state supports fresh-cash test, current-weight initiation test, replaceability/action clock, best alternative/duel status, factor overlap, cash policy and required next action;
- discovery lineage exposes donor lane → UCITS mapping → pricing → fundability status.

### Runbook/output
- one canonical routine path is declared;
- production date is completed-close-derived, not hard-coded to a repair date;
- shadow policies/scenarios do not appear as current controls in NL/EN output;
- NL/EN derive from the same state.

### Governance
- exact-head implementation evidence green;
- independent assurance on frozen candidate returns PASS;
- post-merge exact-main validation green;
- claim and handover close cleanly.

## Evidence contract
Persist or reference:
- exact source/head SHA;
- changed-file list;
- relevant tests and workflow runs;
- client-surface regression evidence;
- donor-parity matrix;
- independent assurance verdict;
- merge SHA and exact-main checks;
- handover disposition.

## Handover contract
The implementation handover must explicitly list completed scope, unresolved items, exact head, tests/evidence, and disposition. Assurance may not mutate the candidate it reviews. Any repair after assurance creates a fresh candidate and requires fresh assurance.
