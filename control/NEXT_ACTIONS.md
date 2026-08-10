# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
ETF_EU_DONOR_CONVERGENCE_V1
```

Authoritative work lineage:

```text
work_package=ETF-EU-WP-DONOR-CONVERGENCE-V1
active_claim=ETF-EU-DONOR-CONVERGENCE-V1
branch=agent/etf-eu-donor-convergence-v1
target=main
prior_frozen_pr=84
prior_frozen_head=888a55b5bc8ae3d465691117157c616893b3addb
prior_assurance_issue=87
prior_assurance=PASS_FOR_FROZEN_HEAD_ONLY
principal_decision_required=false
principal_action_required=false
```

Roadmap:

`docs/roadmaps/WEEKLY_ETF_EU_DONOR_CONVERGENCE_ROADMAP_20260810.md`

## Immediate sequence

### P0 — authority correctness

1. Keep PR #84 frozen; do not merge or modify it.
2. Open one successor PR for `agent/etf-eu-donor-convergence-v1` and bind the active claim to it.
3. Make `config/etf_eu_transition_policy_v1.yml` unambiguously historical/shadow evidence and prevent its percentages from creating current allocation/client authority.
4. Remove current allocator dependence on retired 35% cash and 15% new-position values.
5. Demote the historical 25% turnover and theme caps from current authority; do not invent replacements.
6. Remove the historical two-exposure Stage-1 allowlist as the current allocation gate while preserving its historical activation provenance.
7. Correct embedded-semiconductor wording/typing to measured lower-bound analytics, not a minimum target/control.
8. Reconcile model broker-neutrality: account-level broker permission is real-execution only.
9. Add deterministic fail-closed tests for every P0 defect class.

### P1 — donor-comparable operating behavior

10. Converge the discovery path so broad donor opportunities flow through EU research proxies, exact UCITS mapping, current pricing and fundability without making U.S.-listed ETFs investable.
11. Operationalize the mature capital re-underwriting behavior already present in `control/CAPITAL_REUNDERWRITING_RULES.md` for all current funded EU positions.
12. Make current recommendation memory complete and current-run derived; L0CK must be included.
13. Separate actual portfolio state/current valuation/current recommendation from historical strategic/phase target metadata.
14. Confirm `.github/workflows/run-weekly-etf-eu-routine.yml` as the sole canonical routine-production path and classify date-specific repair/probe/preview paths as non-authoritative evidence/diagnostics.
15. Bind donor macro source commit/as-of date and enforce freshness from evidence date rather than wrapper-generation time.
16. Add a machine-readable donor-parity audit with states `PARITY`, `EU_ADAPTED_PARITY`, `INTENTIONAL_EU_DIVERGENCE`, `GAP_BLOCKING`, `GAP_NONBLOCKING`.

### P2 — maturity/client hygiene

17. Expand persistent EU discovery breadth so the mature donor breadth model is not narrowed to a tiny fixed UCITS front-end list.
18. Operationalize action-clock/replacement-duel/challenger discipline where exact EU candidates and pricing allow it.
19. Keep historical/scenario allocator mechanics outside the current client-control table.

### Release closeout

20. Run complete exact-head CI on the successor candidate.
21. Generate a fresh Dutch-primary/English-companion candidate from one normalized current state.
22. Run full mechanical and rendered-page visual validation.
23. Obtain fresh independent `governance_release_assurance` on the exact successor head/package.
24. If PASS and unchanged, merge the successor, close/supersede PR #84 as read-only evidence, and reconcile work claims/state/roadmap/changelog.
25. Reconcile central `market-predictions/control-plane` freshness/state records.
26. Only then enter a separately governed fresh report production/delivery operation; require real transport plus receipt/attachment evidence before claiming delivery.

## Already completed and not to be repeated

```text
PR78 pricing/product-boundary foundations merged=true
PR82 four-position state-aware preview merged=true
PR80 materially stale and superseded=true
PR84 client-surface repair candidate built=true
PR84 exact-head assurance issue87=PASS
PR84 frozen_evidence=true
convergence_branch_created=true
convergence_roadmap_created=true
convergence_work_package_created=true
convergence_authority_contract_created=true
PR84_to_convergence_handover_created=true
active_release_claim_transferred=true
```

## Prohibited shortcuts

Do not:

- merge PR #84 merely because its narrower assurance passed;
- modify PR #84 and reuse issue #87 PASS;
- replace retired percentages with newly invented percentages;
- use shadow scenarios as current allocation authority;
- fund U.S.-listed donor ETFs in the EU model;
- mutate protected shares/cash while repairing report/runtime authority;
- require broker-account permission for broker-neutral model fundability;
- treat historical target weights as current trade instructions;
- use a hardcoded historical-date repair workflow as routine production authority;
- claim report delivery without a real current-run receipt/attachment manifest;
- leave an ACTIVE claim after its branch/PR is merged, closed or superseded.
