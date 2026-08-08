# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
FINISH_WP_SYNC_11A_OPERATIONAL_PROVIDER_REDUNDANCY
```

The project must finish the existing multi-provider pricing architecture rather than create another price-validation path.

Current state:

```text
work_package=ETF-EU-WP-SYNC-11A_OPERATIONALIZATION_20260808
pull_request=78
state=BLOCKED_EXTERNAL_CREDENTIAL
principal_decision_required=false
principal_action_required=ROTATE_ALPHA_VANTAGE_REPOSITORY_SECRET
```

## Immediate sequence

1. Principal replaces the existing GitHub Actions repository secret `ALPHA_VANTAGE_API_KEY` with a newly issued Alpha Vantage key. The key must never be pasted into chat or committed to the repository.
2. After explicit confirmation that the GitHub secret was replaced, implementation records a non-secret `config/alpha_vantage_key_rotation_confirmed.json` marker.
3. Rerun the repaired WP11A live qualification for report date 2026-08-05 with historical cache disabled.
4. Require the authoritative funded universe to be exactly VWCE, EUNA, SXR8 and L0CK.
5. Require 4/4 funded lines to have at least two providers on the same completed-close date within 1.0% spread and 4/4 exact-line identity anchors.
6. If Alpha Vantage fails any funded line because of symbol coverage, quota, date or identity limitations, keep the gate closed and configure the next viable provider from Leeway, EODHD or Marketstack. Do not return to a parallel Börse/Yahoo production path.
7. Once 4/4 live no-cache consensus passes, rerun `Build fresh governed Weekly ETF EU package` on the exact repaired candidate.
8. Require independent `governance_release_assurance` on the resulting exact candidate before merge or any guarded delivery action.
9. Reconcile `control/CURRENT_STATE.md`, this file, the WP11A operationalization work package, evidence record and durable decision record at closeout.
10. Surface guarded delivery only after the complete current-run package and assurance are valid; delivery remains a separate authority/action layer.

## Already completed in this cycle

```text
funded_universe_state_authority_repair=PASS
stale_L0CK_registry_flag_detection=PASS
deterministic_WP11A_suite=PASS
fresh_package_WP11A_route_regression_test=PASS
canonical_routine_uses_WP11A=true
PR78_fresh_package_uses_WP11A=true
no_cache_live_funded_count=4
no_cache_live_identity_anchors=4/4
no_cache_live_consensus=0/4
protected_state_unchanged=true
```

Evidence:

```text
control/evidence/wp11a_reopen_operational_audit_20260808.md
workflow_run=31258172996
artifact_id=9022002190
fresh_package_run=31258280491
```

## Prohibited shortcuts

Do not:

- weaken the two-provider same-date requirement;
- increase the 1.0% agreement tolerance merely to make a run pass;
- use another venue, share class or proxy as the funded Xetra line;
- treat a static registry `funded` flag as portfolio authority;
- reuse July 31 evidence for August 5;
- reintroduce the old Börse/Yahoo compatibility path as production authority;
- record the Alpha rotation marker before the GitHub secret is genuinely replaced;
- expose any API key in repository content, logs, artifacts or chat;
- claim report delivery from pricing, rendering, SMTP invocation or package generation alone.
