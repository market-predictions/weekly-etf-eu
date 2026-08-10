# ETF EU Work Package — Donor Convergence V1

```text
work_package_id=ETF-EU-WP-DONOR-CONVERGENCE-V1
claim_id=ETF-EU-DONOR-CONVERGENCE-V1
owner_role=implementation_operations
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-donor-convergence-v1
base_evidence_head=888a55b5bc8ae3d465691117157c616893b3addb
created=2026-08-10
risk_class=financial_report_decision_state_and_delivery_boundary
portfolio_mutation_authorized=false
ledger_write_authorized=false
real_broker_execution_authorized=false
delivery_authorized=false
```

## Current issue

Weekly ETF EU has strong EU/UCITS identity, pricing and governance infrastructure, but parts of the decision/allocation runtime still inherit historical transition mechanics that are weaker or inconsistent with the mature Weekly ETF donor.

Material examples:

- shadow-only 35% cash / 15% new-position / 25% turnover / theme-cap values are consumed as allocator controls;
- a fixed two-theme Stage-1 allowlist constrains current allocation review;
- embedded semiconductor overlap is exposed with minimum/control semantics instead of measured-lower-bound semantics;
- runbook broker-permission wording conflicts with broker-neutral model-investability authority;
- current recommendation scorecard is stale and incomplete;
- discovery breadth, re-underwriting and challenger discipline are not operationally converged;
- historical target metadata can be confused with current allocation authority;
- multiple historical/repair workflow paths obscure the singular canonical routine;
- donor macro freshness is not sufficiently bound to immutable source/as-of evidence.

## Root cause

The repository matured through several activation/transition packages. Later report and pricing repairs superseded individual visible defects, but the historical transition allocator remained connected to current report generation. Donor behaviors were copied or adapted in pieces without one explicit convergence contract tying decision framework, input/state contract, output contract, runbook and assurance together.

## Recommended change

Perform one controlled convergence program in three layers:

1. **P0 authority correctness** — remove shadow/retired policy influence and internal contradictions.
2. **P1 operational donor parity** — integrate discovery, mapping, pricing, fundability, re-underwriting, scorecard/state and canonical routine.
3. **P2 maturity/client hygiene** — complete EU-native breadth, action clocks/duels and remove scenario mechanics from client authority surfaces.

The authoritative roadmap is:

`docs/roadmaps/WEEKLY_ETF_EU_DONOR_CONVERGENCE_ROADMAP_20260810.md`

## Exact files initially in scope

Control/authority:

- `control/SYSTEM_INDEX.md`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/WORK_CLAIMS.json`
- `control/DECISION_LOG.md`
- `control/CHANGELOG.md`
- `control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md`
- `control/UCITS_INVESTABILITY_RULES.md` when clarification is required
- `control/CAPITAL_REUNDERWRITING_RULES.md` only for EU adaptation/integration, not U.S. state import
- new `control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md`

Configuration/state:

- `config/etf_eu_transition_policy_v1.yml`
- `config/etf_eu_discovery_universe.yml`
- `config/ucits_benchmark_proxy_map.yml`
- `config/ucits_close_price_validation_basket.yml`
- `output/etf_eu_portfolio_state.json` only for metadata-authority repair; protected shares/cash are immutable in this package
- `output/etf_eu_recommendation_scorecard.csv` only through deterministic current-run derivation, not manual recommendation invention

Runtime:

- `runtime/build_etf_eu_target_allocator_shadow_v3.py`
- `runtime/build_etf_eu_target_allocator_shadow_v3_policy_gate.py`
- client-state/report synchronizers that consume allocator controls
- scorecard/runtime-state builders added or adapted for current-run re-underwriting
- `runtime/adapt_weekly_etf_macro_for_eu.py`

Workflow:

- `.github/workflows/run-weekly-etf-eu-routine.yml`
- validation workflows/tests for the above contracts
- date-specific repair workflows only to mark/quarantine authority, not to rewrite their historical evidence.

## Implementation rules

### Rule 1 — protect validated PR #84 evidence

Do not modify PR #84. It remains frozen at `888a55b5bc8ae3d465691117157c616893b3addb` with issue #87 PASS. This work is a successor candidate and needs fresh assurance.

### Rule 2 — do not replace unsupported caps with new unsupported caps

When a shadow/retired rule is removed, the default result is **no current hard cap from that source**. Any new material portfolio cap requires explicit current authority and recorded rationale.

### Rule 3 — behavior port, not state port

Donor patterns may be ported for:

- broad discovery;
- re-underwriting;
- recommendation memory;
- runtime-state separation;
- bilingual determinism;
- pricing/manifests;
- delivery controls.

Do not port:

- U.S. holdings;
- U.S.-listed fundability;
- donor recipients/secrets;
- donor broker/execution assumptions.

### Rule 4 — current state outranks historical scenario

All runtime decisions must follow the authority order defined in `control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md`.

### Rule 5 — no loose-end closeout

A code change is not complete until:

- its tests are green on the exact head;
- roadmap/work-package acceptance is updated;
- current state and next action are reconciled;
- stable decisions are logged;
- the originating claim ends in `CLOSE`, `TRANSFER`, or `SUPERSEDE` through an explicit handover;
- changed release candidates receive fresh independent assurance.

## Acceptance criteria

### P0

- [ ] 35% minimum cash has zero current allocator/client authority.
- [ ] 15% maximum new ETF/direct position has zero current allocator/client authority.
- [ ] fixed 50% cash-first scenario is internal/historical only.
- [ ] 25% turnover and 18% semiconductor values are not current controls absent explicit authority.
- [ ] embedded semiconductor value is labelled/typed as observed lower bound, not minimum target.
- [ ] model fundability is broker-neutral; broker/account permission is real-execution only.
- [ ] fail-closed tests reject reintroduction of retired/shadow controls.

### P1

- [ ] current allocation review is not hard-frozen to two historical Stage-1 exposures.
- [ ] broad donor discovery can flow through UCITS mapping without allowing U.S. ETFs to become fundable.
- [ ] exact-line pricing/fundability remains mandatory for current funding decisions.
- [ ] all funded holdings appear in current-run recommendation memory.
- [ ] re-underwriting fields are current-run derived and deterministic.
- [ ] actual portfolio state is separated from historical target/scenario metadata.
- [ ] one workflow is explicitly canonical for routine production and uses run-scoped dates.
- [ ] macro donor source identity and evidence date are bound and freshness validated.
- [ ] machine parity audit reports no `GAP_BLOCKING` items.

### P2

- [ ] persistent EU discovery breadth is comparable to donor behavior.
- [ ] action-clock and challenger/duel discipline is operational where evidence allows.
- [ ] client report contains current controls/decisions only; internal scenarios do not masquerade as policy.

### Release/assurance

- [ ] exact successor PR head identified.
- [ ] relevant CI green on exact head.
- [ ] fresh NL/EN candidate built from normalized current state.
- [ ] complete visual review green.
- [ ] independent `governance_release_assurance` returns PASS on exact candidate.
- [ ] no delivery/broker action inferred from generation/assurance.

## Test plan

At minimum add/extend deterministic tests for:

1. retired-policy leakage rejection;
2. non-authoritative shadow-policy typing;
3. dynamic candidate-set behavior;
4. exact UCITS identity/fundability boundaries;
5. broker-neutral model vs execution permission split;
6. lower-bound exposure semantics in NL/EN;
7. recommendation scorecard completeness for all funded tickers;
8. state historical-target authority separation;
9. canonical workflow date/run identity;
10. macro source/as-of freshness;
11. parity-audit completeness;
12. client report Sections 6/13/14/15 consistency;
13. no portfolio quantity/cash mutation from report/review reconstruction.

## Handover route

Opening handover:

`handover/ETF_EU_PR84_TO_DONOR_CONVERGENCE_V1_20260810.md`

Final handover must record:

```text
exact_pr
exact_head
source/test/workflow changes
retired/superseded paths
machine evidence
visual evidence
assurance issue + verdict
portfolio mutation=false unless separately authorized
ledger write=false unless separately authorized
delivery=false unless separately authorized
claim disposition=CLOSE|TRANSFER|SUPERSEDE
remaining gaps=none or explicit nonblocking backlog
```

## Stop/escalation conditions

Escalate to the principal only if execution discovers a genuinely material choice not resolvable from current authority, for example:

- adopting a new hard position/theme/cash/turnover limit;
- changing the investment mandate or starting capital;
- authorizing real broker execution;
- changing recipients/delivery authority;
- deliberately accepting a material donor-parity gap.

Ordinary implementation, documentation, test and reversible architecture choices remain delegated to the coordinator/implementation role.
