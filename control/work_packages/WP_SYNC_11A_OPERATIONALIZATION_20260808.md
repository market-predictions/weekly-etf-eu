# ETF-EU-WP-SYNC-11A operationalization — 2026-08-08

## Objective

Finish operationalizing the already validated WP-SYNC-11A multi-provider completed-close architecture for the current four-position Weekly ETF EU model portfolio and converge every production consumer onto that contract.

## Current issue

The original WP-SYNC-11A closeout proved the architecture for 2026-07-31 and three funded positions using date-bound Alpha Vantage historical corroboration plus Yahoo Chart. It did not prove future-date provider redundancy.

The provider-redundancy blocker is now resolved for report date 2026-08-05 after principal-confirmed Alpha Vantage key rotation. Live evidence subsequently exposed downstream consumers and validators that still encoded the retired provider pair or three-position portfolio assumptions; those are being converged under this operationalization rather than weakening any gate.

## Scope

1. Derive the funded universe from authoritative portfolio state rather than static registry flags.
2. Preserve the two-provider same-date 1.0% spread gate and exact-line identity-anchor requirement.
3. Restore at least one genuinely live second provider for fresh report dates.
4. Re-run live no-cache qualification for all four funded positions.
5. Route governed routine pricing through the proven WP11A qualification path.
6. Converge downstream transition-evidence and allocator consumers onto the WP11A/state contracts.
7. Require fresh independent release assurance for the final exact release candidate.

## Non-goals

- No weakening of price-evidence requirements.
- No proxy venue or share-class substitution.
- No portfolio mutation or ledger write.
- No report delivery or recipient action.
- No commercial data-redistribution authority decision.
- No return to the old Börse/Yahoo compatibility path as production authority.

## Acceptance criteria

```text
funded_universe_authority=output/etf_eu_portfolio_state.json
funded_position_count=4
required_same_date_provider_count=2
agreement_tolerance_pct=1.0
historical_cache_required=false
funded_consensus=4/4
funded_identity_anchors=4/4
protected_state_unchanged=true
PR_fresh_package_uses_wp11a_engine=true
canonical_routine_uses_wp11a_engine=true
transition_consumers_use_wp11a_contract=true
allocator_uses_authoritative_portfolio_state=true
independent_assurance=PASS
```

## Repaired live pricing evidence

After principal-confirmed Alpha Vantage repository-secret rotation and non-secret rotation-marker recording, fresh-package run `31259156975` proved:

```text
report_date=2026-08-05
funded_position_count=4
funded_consensus=4/4
funded_identity_anchors=4/4
historical_cache_used=0
alpha_vantage_live=true
report_pricing_gate_passed=true
```

Observed two-provider close pairs:

```text
VWCE alpha_vantage=168.04 yahoo_chart=168.03999329
EUNA alpha_vantage=4.9116 yahoo_chart=4.91160011
SXR8 alpha_vantage=722.42 yahoo_chart=722.41998291
L0CK alpha_vantage=10.932 yahoo_chart=10.93200016
```

A quota audit then showed the generic engine was spending 24 Alpha calls per qualification (12 identity searches plus 12 close calls). The production policy now reserves Alpha for the four authoritative funded close requests only and performs no Alpha identity-search calls; Yahoo remains the independent exact-line identity anchor. Subsequent live evidence again proved 4/4 consensus with zero historical cache.

## Downstream convergence findings

The restored pricing gate exposed stale downstream assumptions:

1. `pricing/apply_current_close_results_to_transition_evidence.py` expected a specific historical Börse+Yahoo provider pair and indexed legacy `isin` instead of native WP11A `expected_isin`. It now consumes the provider-agnostic WP11A qualified-consensus + exact-line identity-anchor contract.
2. Stage-1 allocator paths treated every candidate as a new trade. In the authoritative four-position state, L0CK is already funded. The allocator now excludes an exact already-funded candidate from incremental cash/turnover/slot sizing, then restores its strategy eligibility with zero duplicate order while counting the existing direct position toward the relevant theme cap.
3. Allocator, transition-replay and allocator-report CI lanes contained hard-coded three-position validator assumptions. They now pass authoritative portfolio state into the allocator and use the activated validator, which delegates unchanged to the legacy validator when the portfolio is not activated.

## Authority boundary

```text
portfolio_mutation=false
ledger_write=false
real_broker_execution=false
delivery_authority=false
secret_value_recorded=false
```

## Status

```text
status=ACTIVE_PRODUCTION_CONVERGENCE
owner=implementation_operations
principal_decision_required=false
external_dependency=none_currently
pricing_blocker=RESOLVED
remaining_gate=fresh_exact_head_package_and_independent_assurance
```
