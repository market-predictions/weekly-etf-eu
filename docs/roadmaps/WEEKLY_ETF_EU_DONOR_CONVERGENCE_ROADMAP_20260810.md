# Weekly ETF EU — Donor Convergence Roadmap

Date: 2026-08-10  
Roadmap ID: `ETF-EU-DONOR-CONVERGENCE-V1`  
Repository: `market-predictions/weekly-etf-eu`  
Upstream donor: `market-predictions/weekly-etf`

## Objective

Close the material architecture and authority gaps between Weekly ETF EU and the mature Weekly ETF donor while preserving EU-specific product authority.

The target is **behavioral parity where the donor is mature**, not repository cloning:

```text
port mature behavior
+ preserve EU/UCITS authority
+ remove legacy transition-policy leakage
+ make every current allocation/report rule traceable to current authority
```

The roadmap is complete only when the canonical Weekly ETF EU routine can run from current state through discovery, UCITS mapping, pricing, re-underwriting, report generation, independent assurance and guarded delivery without relying on retired or shadow allocation rules.

## Non-negotiable boundaries

Preserve:

- ISIN-first identity;
- exact share class + venue + exchange trading line + trading currency;
- UCITS and PRIIPs/KID gates;
- U.S.-listed ETFs as research proxies only;
- broker-neutral model-investability;
- multi-provider completed-close evidence;
- Dutch-primary + English-companion output from one normalized state;
- model portfolio separate from real broker execution;
- independent governance/release assurance;
- receipt/attachment evidence before `DELIVERY_CONFIRMED`.

Do not:

- import U.S. portfolio state or recipient authority;
- invent replacement allocation caps;
- mutate protected shares/cash merely to make reports look aligned;
- use shadow/scenario percentages as current portfolio authority;
- reuse an assurance verdict after the assured candidate changes.

## Current baseline and lineage

The convergence line starts from exact assured PR #84 head:

```text
pr84_frozen_head=888a55b5bc8ae3d465691117157c616893b3addb
pr84_assurance_issue=87
pr84_assurance_verdict=PASS
successor_branch=agent/etf-eu-donor-convergence-v1
```

PR #84 remains frozen evidence. The convergence line requires a new exact-head PR and fresh assurance because this roadmap addresses broader defect classes outside issue #87 scope.

---

# P0 — Authority correctness before release or delivery

## P0.1 Remove transition-policy authority leakage

Current defect:

`config/etf_eu_transition_policy_v1.yml` declares itself `shadow_only`, `funding_authority=false`, `execution_authority=false`, but its percentages are consumed by allocator/report paths.

Required result:

- historical transition-policy values remain reproducible evidence only;
- no current allocator budget or client control derives from:
  - 35% minimum cash;
  - 15% maximum new ETF/direct position;
  - fixed 50% cash-first scenario;
  - 25% turnover ceiling unless separately authorized;
  - 18% semiconductor cap unless separately authorized;
- no replacement cap is invented.

Acceptance:

```text
retired_35_cash_runtime_effect=false
retired_15_new_position_runtime_effect=false
fixed_50_cash_client_control=false
shadow_25_turnover_current_authority=false
shadow_18_semiconductor_current_authority=false
```

## P0.2 Correct embedded-exposure semantics

The approximately 3.10% semiconductor value is a measured lower bound from documented overlap, not a minimum portfolio target.

Required client meaning:

```text
measured embedded semiconductor exposure lower bound
```

Acceptance:

- NL/EN report surfaces cannot describe it as a required minimum or allocation control;
- machine state preserves methodology and lower-bound warning.

## P0.3 Resolve broker-neutrality contradiction

Canonical model rule:

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

Required:

- model investability/fundability does not require account-level broker permission;
- real execution remains blocked without broker/account permission.

## P0.4 Establish one explicit allocation-authority contract

Authority order:

```text
explicit current allocation decision
> protected portfolio state and trade ledger
> current completed-close valuation
> current re-underwriting/fundability evidence
> donor opportunity state
> historical strategy context and shadow scenarios
```

Retired/shadow data must never outrank current state.

### P0 release gate

No merge or delivery until exact-head tests prove all P0 items and independent assurance returns `PASS`.

---

# P1 — Donor parity in decision, state and routine runtime

## P1.1 Discovery → UCITS mapping → pricing → fundability convergence

Port the mature donor discovery behavior while keeping EU instruments authoritative.

Required sequence:

```text
donor/open breadth discovery
→ research-proxy lanes
→ exact UCITS candidate mapping
→ UCITS/KID/exact-line eligibility
→ current completed-close pricing
→ liquidity/tradability evidence
→ fundability state
→ capital re-underwriting
```

Required breadth behavior should be comparable to the donor:

- broad persistent bucket taxonomy;
- 10–15 candidate lanes where evidence allows;
- challenger rotation;
- relative-strength/liquidity evidence where available;
- compact client publication after broad internal assessment.

A missing UCITS equivalent blocks funding, not research coverage.

## P1.2 Replace frozen two-theme Stage-1 as current allocation gate

Historical Stage-1 remains provenance only.

Current routine allocation review must evaluate the currently eligible mapped opportunity set rather than permanently freezing selection to:

```text
ai_compute_infrastructure
cyber_security
```

No candidate becomes funded automatically. Every new allocation still requires current identity, investability, pricing, concentration/overlap and explicit run-scoped allocation evidence.

## P1.3 Make capital re-underwriting operational

Use the mature donor discipline already present in `control/CAPITAL_REUNDERWRITING_RULES.md`, adapted to UCITS identity and fundability.

Every funded holding receives current-run fields for at least:

- would initiate today;
- would initiate at current weight;
- thesis score/status;
- implementation score/status;
- contribution/drag;
- factor/overlap flag;
- hedge/ballast validity where relevant;
- cash-policy implication;
- replaceable status and review age;
- best mapped/fundable alternative where available;
- required next action;
- explicit override reason when applicable.

## P1.4 Repair recommendation-memory authority

`output/etf_eu_recommendation_scorecard.csv` must be current-run derived and include every funded position, including L0CK.

Stale scorecard rows may remain historical records, but cannot masquerade as the current review.

## P1.5 Reconcile portfolio-state layers

Protected quantities/cash remain authoritative.

Historical target fields such as `strategic_target_weight_pct` or `phase_target_weight_pct` must be explicitly classified as historical strategy context unless a current allocation decision reauthorizes them.

Normalized current-run state must make these distinct:

```text
actual state
current valuation
current recommendation
current allocation decision
historical target/scenario metadata
```

## P1.6 Canonicalize production path

Current production authority:

```text
.github/workflows/run-weekly-etf-eu-routine.yml
```

Date-specific repair, preview, probe and historical send workflows must be explicitly classified as diagnostic/evidence/compatibility paths and must not silently become routine authority.

The canonical routine must:

- use request/run-scoped completed-close dates;
- never depend on a hardcoded historical report date;
- build one normalized state;
- generate NL/EN from the same state;
- run machine + visual gates;
- run independent release assurance before guarded transport.

## P1.7 Macro provenance/freshness

EU macro adaptation must bind:

- donor source commit or immutable source identity;
- donor evidence/as-of date;
- EU report date;
- freshness result.

Wrapper generation time cannot make stale donor evidence fresh.

### P1 parity gate

Produce a machine-readable parity audit that marks each donor capability as:

```text
PARITY
EU_ADAPTED_PARITY
INTENTIONAL_EU_DIVERGENCE
GAP_BLOCKING
GAP_NONBLOCKING
```

No P1 item may remain `GAP_BLOCKING` at convergence closeout.

---

# P2 — Maturity and client-surface simplification

## P2.1 EU-native discovery overlay

Expand durable UCITS mapping breadth so donor lanes can be translated into exact European instruments without shrinking research coverage to a tiny fixed set.

## P2.2 Action-clock and challenger discipline

Operationalize donor-style inertia controls and direct alternative duels without importing U.S. ticker assumptions.

## P2.3 Client-surface authority hygiene

Keep scenario allocators, historical transition rules, internal score mechanics and incomplete lower-bound analytics out of the client-control table.

Client output should show only:

- actual portfolio state;
- current recommendations/decisions;
- material current constraints with explicit authority;
- watch/trigger items;
- transparent evidence limitations.

---

# Execution and documentation model

Every implementation slice must follow:

```text
roadmap item
→ work-package acceptance criterion
→ scoped source/config/test change
→ exact-head CI evidence
→ update current-state/next-actions/changelog
→ handover/disposition
→ independent assurance
```

Required lifecycle records:

- roadmap: this file;
- active work package: `control/work_packages/ETF_EU_WP_DONOR_CONVERGENCE_V1_20260810.md`;
- authority contract: `control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md`;
- claim registry: `control/WORK_CLAIMS.json`;
- lineage handover: `handover/ETF_EU_PR84_TO_DONOR_CONVERGENCE_V1_20260810.md`;
- state: `control/CURRENT_STATE.md`;
- next actions: `control/NEXT_ACTIONS.md`;
- stable decisions: `control/DECISION_LOG.md`;
- implementation history: `control/CHANGELOG.md`;
- final convergence handover/closeout after assurance.

# Definition of done

The convergence program is closed only when:

1. all P0 items pass exact-head regression tests;
2. no retired/shadow fixed percentage can create current allocation or client-control authority;
3. current allocation review is not frozen to the historical two-theme Stage-1 set;
4. every funded holding is represented in current re-underwriting memory;
5. discovery, UCITS mapping, pricing and fundability are one traceable pipeline;
6. portfolio actual state is separated from historical target/scenario metadata;
7. the canonical routine is dynamic and singularly authoritative;
8. macro provenance is date/commit bound;
9. parity audit has no blocking gaps;
10. NL/EN candidate passes machine and complete visual review;
11. fresh independent `governance_release_assurance` returns `PASS` on the exact successor candidate;
12. claim and branch lifecycle is closed/transferred with an explicit handover;
13. project-local and central Control state are reconciled;
14. delivery is performed only as a separate guarded operation with real receipt/attachment evidence if requested.
