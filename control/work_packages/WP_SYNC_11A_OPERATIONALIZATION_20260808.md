# ETF-EU-WP-SYNC-11A operationalization — 2026-08-08

## Objective

Finish operationalizing the already validated WP-SYNC-11A multi-provider completed-close architecture for the current four-position Weekly ETF EU model portfolio.

## Current issue

The original WP-SYNC-11A closeout proved the architecture for 2026-07-31 and three funded positions using date-bound Alpha Vantage historical corroboration plus live Yahoo Chart. It did not prove future-date provider redundancy.

The internal state and routing defects discovered during the reopen are now repaired. The remaining blocker is external: the existing Alpha Vantage repository secret must be rotated before the safety layer may re-enable that provider.

## Scope

1. Derive the funded universe from authoritative portfolio state rather than static registry flags.
2. Preserve the two-provider same-date 1.0% spread gate and exact-line identity-anchor requirement.
3. Restore at least one genuinely live second provider for fresh report dates.
4. Re-run live no-cache qualification for all four funded positions.
5. Route governed PR fresh-package pricing and canonical routine pricing through the same WP11A qualification path.
6. Require fresh independent release assurance for the repaired release candidate.

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
independent_assurance=PASS
```

## Completed internal work

```text
funded_universe_state_authority_repair=PASS
stale_L0CK_registry_flag_detection=PASS
deterministic_WP11A_suite=PASS
repaired_four_position_live_contract=PASS
protected_state_proof=PASS
PR_fresh_package_WP11A_convergence=PASS
no_cache_identity_anchors=4/4
```

Evidence:

```text
control/evidence/wp11a_reopen_operational_audit_20260808.md
initial_live_audit_run=31255211953
repaired_live_audit_run=31258172996
repaired_live_audit_artifact=9022002190
repaired_live_audit_sha256=c91db0567da886eb83f4c1dbf67e44a5604da107ed92b4f543e1fa980153786b
fresh_package_route_run=31258280491
fresh_package_diagnostics_artifact=9022036048
```

## External dependency

```text
required_action=replace_GitHub_Actions_secret_ALPHA_VANTAGE_API_KEY_with_new_key
rotation_marker_present=false
alpha_vantage_live_enabled=false
other_keyed_providers_configured=false
fallback_order=Leeway,EODHD,Marketstack
```

The rotation marker must not be committed before explicit confirmation that the GitHub secret has been replaced. Secret values must never be pasted into chat, repository files, logs or evidence artifacts.

## Status

```text
status=BLOCKED_EXTERNAL_CREDENTIAL
owner=implementation_operations
principal_decision_required=false
principal_action_required=ROTATE_ALPHA_VANTAGE_REPOSITORY_SECRET
safe_internal_work_remaining_before_rotation=NONE_MATERIAL
```
