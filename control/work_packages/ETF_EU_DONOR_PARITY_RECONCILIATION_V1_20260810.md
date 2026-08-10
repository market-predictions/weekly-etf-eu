# ETF EU Donor-Parity Reconciliation V1

Work package: `ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1`
Issue: #90
PR: #91
Owner role: `implementation_operations`
Target: `main`
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`
Status: `IMPLEMENTATION_COMPLETE_PENDING_EXACT_HEAD_ASSURANCE`

## Problem statement
The EU product had strong UCITS/pricing/governance foundations but still contained transition-era authority and maturity gaps relative to the mature Weekly ETF donor. Shadow-only values could leak into allocator/report semantics, broker-neutrality was contradicted by old controls, recommendation memory was incomplete, and discovery/state/runbook convergence was fragmented.

A further P0 defect discovered during execution was a post-normalization funded renderer that reintroduced historical three-position, 7.50% reserve-floor and strategic/phase-target copy after the normalized state had already removed those semantics.

A final operational gap was a historical 2026-07-27 allocator `sister report` workflow that still rendered a parallel client-like report from the historical transition allocator. Its research evidence was non-authoritative, but the executable report surface created ambiguity. The workflow is now retired as `.yml.disabled` and removed from the active donor pin.

## Scope completed
1. Allocation-authority repair.
2. Donor-parity decision/state contract.
3. Client-output authority and renderer repair.
4. Discovery/fundability parity.
5. Macro and completed-close provenance.
6. Canonical candidate/assurance/delivery runbook convergence.
7. Historical workflow disablement and delivery hardening.
8. Machine-preflight vs independent-assurance separation.
9. Donor-pin reconciliation after retirement of the sister-report route.
10. Deterministic regressions and lifecycle documentation.

## Protected boundaries
Throughout implementation:
- no protected portfolio state mutation;
- no trade-ledger write;
- no real broker execution;
- no report delivery or SMTP action;
- no weakening of UCITS/KID/ISIN/exact-line/two-provider funded pricing controls.

## Acceptance criteria and implementation evidence

### Authority — COMPLETE
- 50% maximum position, 35% minimum cash and 15% maximum new ETF are non-executable historical/shadow data.
- 75% is pricing-coverage context, not a position cap.
- 25% turnover and 18% semiconductor cap are research/shadow only unless separately adopted.
- embedded exposure is descriptive lower-bound evidence, never a required minimum/control.
- historical CAP01/transition target weights are removed from normalized live position fields and preserved only as non-current audit metadata.
- donor cash and factor thresholds are review/disclosure triggers, not allocation caps.

Primary evidence:
- `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`
- `runtime/apply_etf_eu_donor_parity_contract.py`
- `tests/test_etf_eu_donor_parity_contract.py`

### Broker-neutrality — COMPLETE
- model investability does not require account-level broker permission;
- real execution may require broker permission;
- authority contract, runtime and runbook agree.

### Donor-parity decision/state — COMPLETE
Every funded holding, including L0CK, is represented in current per-run recommendation memory with:
- would-initiate-today;
- would-initiate-at-current-weight;
- fresh-cash implication;
- thesis/implementation score;
- replaceability/action clock;
- best alternative and replacement close/duel state;
- contribution/drag;
- factor overlap;
- hedge/ballast validity;
- cash-policy implication;
- override/next-review data;
- required next action.

Missing evidence is explicitly `UNRESOLVED`; historical `last_action`, old purchase or old target weights cannot create an implicit Hold.

### Discovery/fundability — COMPLETE
Lineage is explicit:

`donor discovery → research proxy → UCITS mapping → ISIN/KID/exact line → pricing → re-underwriting → explicit allocation decision`

Mapping/pricing alone cannot fund a position.

### Client output — COMPLETE
- normalized allocation map is authoritative;
- funded renderer no longer rebuilds CAP01 allocation semantics;
- current position count is dynamic and includes all four protected positions;
- current-position table contains no strategic/phase target column;
- renderer fails closed on retired reserve/target/three-position phrases and on a missing funded ticker;
- NL/EN render from the same normalized state;
- the obsolete allocator sister-report workflow cannot create a second client-like output surface from historical policy.

Primary evidence:
- `runtime/render_etf_eu_client_grade_v2_funded.py`
- `tests/test_etf_eu_funded_renderer_authority.py`
- `.github/workflows/validate-etf-eu-allocator-report-shadow.yml.disabled`

### Runbook/workflow authority — COMPLETE
- one candidate-only route is canonical;
- candidate route refuses main, cannot self-assure and cannot deliver;
- completed-close date is dynamically resolved;
- twenty historical mutation/send/repair/preview/client-like shadow workflows are `.yml.disabled`;
- exactly three immutable-donor synchronization workflows remain active as research-only validators;
- the donor pin explicitly records the allocator sister-report workflow as retired;
- controlled transport is the only active real delivery route;
- delivery requires exact independent PASS, approved commit lineage, principal send authority and six artifact SHA-256 bindings;
- controlled transport sends exact approved artifacts and does not re-render.

Primary evidence:
- `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`
- `.github/workflows/run-weekly-etf-eu-routine.yml`
- `.github/workflows/send-weekly-etf-eu-controlled-transport.yml`
- `config/weekly_etf_donor_contract_pin.json`
- `tools/validate_weekly_etf_donor_contract_pin.py`
- `tools/validate_etf_eu_guarded_delivery_authority.py`
- `tools/validate_etf_eu_workflow_authority.py`

### Assurance semantics — COMPLETE
Historical machine tooling named `release_assurance` is retained only for compatibility but now produces/validates `etf_eu_release_evidence_preflight`:
- machine PASS is supporting evidence only;
- independent assurance verdict must be null in machine evidence;
- merge authority false;
- delivery authority false;
- a separate `governance_release_assurance` reviewer remains mandatory.

### Governance closeout — PENDING ROLE-B
Remaining release gates:
- final exact-head CI green after administrative closeout commits;
- implementation handover followed by an exact frozen PR-head read;
- independent assurance `PASS | FAIL | INDETERMINATE` on that exact frozen head;
- merge only after PASS and unchanged head;
- exact-main validation;
- issue/claim/project/control-plane closeout.

## Evidence contract
Persist/reference:
- last validated pre-handover implementation head and exact-head workflow runs in the handover;
- the resulting exact frozen PR head in the assurance issue;
- PR #91 changed-file list;
- donor-parity matrix in the roadmap;
- client-surface regression evidence;
- independent assurance verdict;
- merge SHA and exact-main checks;
- final handover disposition.

## Handover contract
The implementation handover is the last repository mutation on the candidate line. It must explicitly list completed scope, unresolved items, last validated pre-handover head, tests/evidence and disposition `HANDOVER_READY`. The resulting PR head containing that handover is then read live and bound by the independent assurance issue. Assurance may not mutate the candidate it reviews. Any repair after assurance creates a fresh candidate and requires fresh assurance.
