# Handover — PR #84 to ETF EU Donor Convergence V1

Date: 2026-08-10  
Disposition: `SUPERSEDE` for further implementation  
Prior line: `ETF-EU-RELEASE-INTEGRATION-V3`  
Successor line: `ETF-EU-DONOR-CONVERGENCE-V1`

## Prior frozen evidence

```text
pull_request=84
branch=agent/etf-eu-release-integration-v3
frozen_head=888a55b5bc8ae3d465691117157c616893b3addb
assurance_issue=87
assurance_verdict=ETF_EU_PR84_V3_RELEASE_ASSURANCE_REVERIFY: PASS
```

PR #84 successfully repaired the client-surface defect class in its assurance scope, including the stale visible 15% maximum-new-ETF row, four-position consistency, pricing identity and NL/EN report coherence.

The PASS remains valid evidence for that exact frozen candidate only.

## Why the line is superseded instead of extended or merged

A broader donor-vs-EU architecture review after the narrow assurance found material defect classes outside issue #87 scope:

1. the historical/shadow transition policy still feeds current allocator mechanics;
2. retired 35% cash and 15% new-position values, plus non-authoritative 25% turnover/theme caps, can influence preferred allocation scenarios;
3. current allocation review is frozen to two historical Stage-1 exposures;
4. approximately 3.10% embedded semiconductor overlap is analytical lower-bound evidence, not a minimum/control;
5. broker-neutral investability and runbook broker-permission requirements conflict;
6. recommendation memory is stale/incomplete and does not include all funded positions;
7. donor discovery/re-underwriting maturity is not yet operationally converged;
8. portfolio actual state and historical target/scenario metadata need clearer authority separation;
9. canonical routine authority needs stronger separation from historical/date-specific repair workflows;
10. macro provenance/freshness requires immutable donor source/as-of binding.

Merging PR #84 and then repairing these items would create unnecessary lineage churn. Modifying PR #84 would invalidate the exact-head assurance. Therefore the safe lifecycle action is to fork a clean successor from the exact assured head and require a new assurance decision after convergence.

## Successor

```text
branch=agent/etf-eu-donor-convergence-v1
base_evidence_head=888a55b5bc8ae3d465691117157c616893b3addb
target=main
work_package=ETF-EU-WP-DONOR-CONVERGENCE-V1
roadmap=docs/roadmaps/WEEKLY_ETF_EU_DONOR_CONVERGENCE_ROADMAP_20260810.md
authority_contract=control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md
```

## Material inherited evidence to preserve

The successor inherits the validated PR #84 behavior as a starting point:

- exact four funded positions: VWCE, EUNA, SXR8, L0CK;
- protected shares and cash;
- 4/4 funded same-date two-provider completed-close consensus on the certified package;
- 4/4 exact-line identity anchors;
- product-boundary separation from Weekly FX;
- client-surface consistency fixes for Sections 6/13/14/15;
- NL/EN package render integrity;
- model-only/no real broker execution boundary.

These are inherited implementation/evidence facts, not automatic approval of the changed successor head.

## Authority boundary for successor work

```text
portfolio_mutation_authorized=false
ledger_write_authorized=false
real_broker_execution_authorized=false
delivery_authorized=false
recipient_change_authorized=false
new_hard_allocation_caps_authorized=false
```

The successor may repair authority semantics, runtime plumbing, discovery/re-underwriting, state normalization, tests, workflows and client output without mutating protected portfolio quantities/cash.

## Required successor closeout

Before this handover can be considered fully consumed:

1. update `control/WORK_CLAIMS.json` so only the successor integration claim remains ACTIVE;
2. open a successor PR targeting current `main`;
3. implement the roadmap P0/P1/P2 scope or explicitly classify residual nonblocking items;
4. run exact-head CI and parity audit;
5. build a fresh NL/EN candidate;
6. obtain fresh independent `governance_release_assurance` on the exact successor candidate;
7. close/supersede PR #84 without deleting its evidence;
8. reconcile project-local and central Control state;
9. end the successor claim via explicit `CLOSE`, `TRANSFER`, or `SUPERSEDE` handover.

## Final disposition

```text
prior_claim=ETF-EU-RELEASE-INTEGRATION-V3
prior_line_disposition=SUPERSEDED_READ_ONLY_EVIDENCE
successor_claim=ETF-EU-DONOR-CONVERGENCE-V1
successor_status=ACTIVE
```
