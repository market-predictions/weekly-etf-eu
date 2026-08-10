# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-10
repository=market-predictions/weekly-etf-eu
live_main_at_opening=76325f60a3abcda4a059f7823c9c0b5024802870
operating_mode=ROUTINE_WEEKLY_ETF_EU_PRODUCTION_WITH_INDEPENDENT_RELEASE_ASSURANCE
state=DONOR_CONVERGENCE_IMPLEMENTATION_ACTIVE
current_work_package=ETF-EU-WP-DONOR-CONVERGENCE-V1
active_claim=ETF-EU-DONOR-CONVERGENCE-V1
working_branch=agent/etf-eu-donor-convergence-v1
prior_frozen_pull_request=84
prior_frozen_head=888a55b5bc8ae3d465691117157c616893b3addb
prior_assurance_issue=87
prior_assurance_verdict=PASS
principal_decision_required=false
principal_action_required=false
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

## Current objective

Converge Weekly ETF EU on the mature Weekly ETF donor behavior for discovery, capital re-underwriting, recommendation memory, normalized state and routine execution while preserving EU-specific UCITS/investability authority.

The current priority is no longer to merge PR #84. PR #84 is frozen assured evidence. A broader architecture audit discovered material authority/runtime gaps outside issue #87 scope, so the clean successor line is:

```text
branch=agent/etf-eu-donor-convergence-v1
roadmap=docs/roadmaps/WEEKLY_ETF_EU_DONOR_CONVERGENCE_ROADMAP_20260810.md
work_package=control/work_packages/ETF_EU_WP_DONOR_CONVERGENCE_V1_20260810.md
authority_contract=control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md
handover=handover/ETF_EU_PR84_TO_DONOR_CONVERGENCE_V1_20260810.md
```

## Why PR #84 is not merged

Issue #87 correctly returned PASS for exact frozen head `888a55b5bc8ae3d465691117157c616893b3addb` within its release-assurance scope.

A later donor-vs-EU architecture audit established additional defect classes:

1. shadow transition-policy percentages still influence allocator mechanics;
2. retired 35% minimum cash and 15% maximum-new-position semantics remain in historical preferred allocation machinery;
3. 25% turnover and theme caps have no current authority but can be presented/used as controls;
4. the historical two-theme Stage-1 allowlist constrains current allocation review;
5. embedded semiconductor overlap is analytical lower-bound evidence, not a minimum/control;
6. broker-neutral investability conflicts with runbook account-permission wording;
7. recommendation memory is stale/incomplete;
8. discovery, re-underwriting and challenger discipline are not operationally donor-comparable;
9. actual portfolio state and historical target/scenario metadata require stronger separation;
10. canonical routine and macro-provenance authority need convergence.

Changing PR #84 would invalidate its exact-head PASS. Merging it before fixing the broader defects would create avoidable release churn. It is therefore superseded for further implementation but preserved read-only as evidence.

## Authoritative protected portfolio

Authority:

```text
output/etf_eu_portfolio_state.json
```

Protected funded model positions:

| Ticker | ISIN | Venue | Shares |
|---|---|---|---:|
| VWCE | IE00BK5BQT80 | Xetra | 151 |
| EUNA | IE00BDBRDM35 | Xetra | 1,526 |
| SXR8 | IE00B5BMR087 | Xetra | 10 |
| L0CK | IE00BG0J4C88 | Xetra | 934 |

```text
cash_eur=50208.40
funded_position_count=4
vvsm_status=monitored_unfunded
model_portfolio_only=true
real_broker_execution=false
```

This convergence package may repair metadata/authority separation but may not mutate protected shares, cash or the trade ledger.

## Current allocation authority

Canonical contract:

`control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md`

Authority order:

```text
explicit current allocation decision
> protected portfolio state and trade ledger
> current completed-close valuation and exact-line identity
> current re-underwriting/overlap/fundability evidence
> current donor opportunity state after EU mapping
> historical strategy context, transition scenarios and prior reports
```

Retired/non-authoritative controls:

```text
50% maximum position=RETIRED_UNSUPPORTED_SHADOW_RULE
35% minimum cash=RETIRED_UNSUPPORTED_SHADOW_RULE
15% maximum new ETF=RETIRED_UNSUPPORTED_SHADOW_RULE
75%=PRICING_COVERAGE_CONTEXT_NOT_POSITION_CAP
25% turnover transition value=CURRENT_AUTHORITY_FALSE
18% semiconductor transition cap=CURRENT_AUTHORITY_FALSE
historical Stage-1 maximum positions=CURRENT_AUTHORITY_FALSE_UNLESS_SEPARATELY_DECIDED
```

No replacement numerical hard caps have been authorized.

## Diagnosed current runtime root cause

`config/etf_eu_transition_policy_v1.yml` declares itself shadow-only but its values are consumed by:

```text
runtime/build_etf_eu_target_allocator_shadow_v3.py
runtime/build_etf_eu_target_allocator_shadow_v3_policy_gate.py
```

The base shadow allocator calculates its preferred scenario from turnover, cash reserve, direct-position and theme caps. The policy gate further requires exactly:

```text
ai_compute_infrastructure
cyber_security
```

This historical scenario machinery must remain reproducible where useful but must not drive current allocation/client authority.

## Strong foundations to preserve

Already established and not to be weakened:

- ISIN-first UCITS identity;
- exact trading-line verification;
- UCITS and PRIIPs/KID gates;
- U.S. ETFs as research proxies only;
- funded same-date multi-provider completed-close consensus;
- exact-line identity anchors;
- broker-neutral model portfolio;
- Dutch-primary + English-companion package;
- Weekly FX product-boundary separation;
- independent release assurance;
- delivery receipt/attachment evidence before `DELIVERY_CONFIRMED`.

## Current release gate

No report delivery or merge is authorized from this convergence state.

Required sequence:

```text
P0 authority repair
→ P1 donor-parity/runtime convergence
→ P2 client/maturity closeout
→ exact-head CI + parity audit
→ fresh NL/EN candidate
→ complete visual validation
→ fresh independent governance_release_assurance
→ merge only on PASS and unchanged head
→ separately governed fresh production run/delivery if requested
```

## Principal boundary

No principal decision is currently required. Existing authority is sufficient to remove stale/shadow rules, converge donor behavior, improve state/runtime separation and add fail-closed tests.

Escalate only if a new hard portfolio limit, mandate change, real broker execution, recipient/delivery change or deliberate acceptance of a material blocking gap becomes necessary.
