# ETF EU Allocation Authority Convergence V1

Date: 2026-08-10  
Status: canonical project-local authority contract  
Scope: Weekly ETF EU model-portfolio allocation, recommendation and client-control authority

## Purpose

Prevent historical transition scenarios, shadow allocators, donor targets, stale report prose or broker-execution metadata from silently becoming current ETF EU portfolio authority.

This contract does not create a new allocation policy. It resolves authority among existing sources and explicitly demotes unsupported legacy/shadow percentages.

## Current authority order

For a Weekly ETF EU run, resolve allocation and recommendation facts in this order:

```text
1. explicit current allocation decision for the exact run/candidate
2. protected portfolio state and trade ledger
3. current completed-close valuation and exact-line identity evidence
4. current re-underwriting, overlap/concentration and fundability evidence
5. current donor opportunity/discovery state after EU mapping
6. historical strategy context, transition scenarios and prior reports
```

Lower-ranked sources may explain or compare. They may not override higher-ranked current facts.

## Protected state rule

Without separate explicit allocation authority, report/review/convergence work must preserve:

```text
shares
cash
trade ledger
model_portfolio_only=true
real_broker_execution=false
```

Historical target weights do not authorize a trade.

## Retired unsupported shadow rules

The following are not current Weekly ETF EU portfolio constraints:

```text
50% maximum position
35% minimum cash
15% maximum new ETF/direct position
75% position cap
```

The `75%` value belongs only to historical pricing-coverage context where applicable; it is not a position-weight cap.

Any runtime or client surface that promotes these values as current controls must fail closed.

## Historical transition-policy values

`config/etf_eu_transition_policy_v1.yml` is historical/shadow transition evidence.

Values such as:

```text
maximum_gross_turnover_pct_nav=25
minimum_post_stage_cash_pct_nav=35
maximum_new_direct_position_pct_nav=15
ai_compute_infrastructure theme cap=18
cyber_security theme cap=15
staged cash-first 50% comparison
```

may remain for reproducibility of historical Stage-1 scenario analysis, but have:

```text
current_allocation_authority=false
current_funding_authority=false
client_control_authority=false
real_execution_authority=false
```

The 25% turnover and theme-cap values are not promoted to current authority merely because they were previously useful scenario assumptions. A new hard turnover/theme limit requires an explicit recorded current decision.

## Position-count authority

A donor rule is not automatically an EU rule.

Until an explicit current ETF EU decision establishes a hard maximum active-position count, any historical `maximum_positions` value in transition/shadow policy is non-authoritative for current funding.

The current run may still report position count and concentration. A new hard maximum requires a separately recorded decision because it materially constrains capital allocation.

## Embedded-exposure semantics

Holdings-overlap analysis provides an observed lower bound when underlying holdings coverage is incomplete.

Therefore values such as the approximately 3.10% embedded semiconductor exposure are:

```text
analytic_type=measured_exposure_lower_bound
allocation_target=false
minimum_required_exposure=false
hard_cap=false
funding_authority=false
```

Client wording must say `measured lower bound` / `gemeten ondergrens` or equivalent and must not label this figure as a required minimum/control.

## Cash discipline

The mature donor behavior that cash must be actively explained is valid as decision discipline, not a fixed EU cash target.

For current ETF EU reviews:

- cash is an active portfolio state and must be classified/explained;
- actionable fundable opportunities should trigger a deploy-or-explain review;
- no fixed minimum or maximum cash percentage is implied by this contract;
- blocked/unmapped/unpriced capacity remains cash rather than being force-allocated.

## Concentration and overlap discipline

The donor pattern of explicitly reviewing concentration/factor overlap is imported as behavior.

This contract does not create a numerical ETF EU concentration cap. Current overlap evidence should inform re-underwriting and risk explanation; a numerical hard cap requires explicit current authority.

## Broker-neutral model boundary

Model investability is broker-neutral:

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

A candidate can be model-investable/fundable when UCITS/KID/identity/exact-line/pricing/liquidity and current allocation gates pass even if no account-specific broker mapping has been verified.

A real order cannot be authorized without the applicable broker/account permission and execution mapping.

## Donor opportunity boundary

The donor can provide:

- broad discovery;
- lane ranking;
- structural/macro context;
- relative-strength/challenger evidence;
- behavioral re-underwriting patterns.

The donor cannot provide ETF EU funding authority by itself.

Funding requires an exact EU/UCITS candidate and current EU gates.

## Report/output rule

The client report may present only:

1. actual current portfolio state;
2. current recommendations and run-scoped decisions;
3. current authoritative constraints;
4. measured risk/overlap analytics clearly labelled as analytics;
5. scenarios explicitly labelled non-authoritative when genuinely client-useful.

Internal historical transition scenarios should normally remain outside the client-control table.

## Machine enforcement

Current runtime/validation should expose or infer fields equivalent to:

```text
allocation_authority_source
shadow_policy_used_for_current_allocation=false
retired_fixed_percentage_used=false
historical_target_used_for_current_trade=false
embedded_exposure_semantics=measured_lower_bound
broker_specific_permission_required_for_model=false
real_broker_execution=false
```

A contradictory state must fail the release gate.

## Change rule

This contract may be changed only through a reviewed project decision because it defines allocation authority precedence.

New numerical portfolio constraints require explicit rationale and decision evidence; they may not be introduced as an implementation convenience or inherited donor default.
