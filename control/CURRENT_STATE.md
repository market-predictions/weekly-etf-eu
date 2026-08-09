# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-09
repository=market-predictions/weekly-etf-eu
main_sha_at_reconciliation=93dbe7450e44d22a2fe247a8d1f1ffb9e07adf3c
operating_mode=ROUTINE_WEEKLY_ETF_EU_PRODUCTION_WITH_INDEPENDENT_RELEASE_ASSURANCE
current_work_package=ETF-EU-WP-RELEASE-INTEGRATION-V3
active_claim=ETF-EU-RELEASE-INTEGRATION-V3
working_branch=agent/etf-eu-release-integration-v3
superseded_pull_request=80
superseded_head=01fb4e9238d1921dc8fd52ad552d3acba5bfceea
state=ACTIVE_CLIENT_GRADE_RELEASE_REPAIR
principal_decision_required=false
principal_action_required=false
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

## Current objective

Reconstruct one clean Weekly ETF EU release line from current `main`, carrying forward only the still-relevant PR #80 remediation deltas. Then prove the resulting exact head through product-boundary, allocation-lineage, completed-close pricing/replay, client-surface and report gates; generate a fresh Dutch/English candidate; and obtain fresh independent release assurance.

The project must not continue accumulating on PR #80. Its branch is now read-only implementation/evidence donor material under the canonical work-claim lifecycle standard.

## Why the integration line changed

Live comparison at reconciliation showed PR #80 had materially diverged from `main`:

```text
pr80_head=01fb4e9238d1921dc8fd52ad552d3acba5bfceea
main=93dbe7450e44d22a2fe247a8d1f1ffb9e07adf3c
status=diverged
ahead_by=95
behind_by=147
merge_base=050bf08506b54400615538feeca272fbf967ed82
```

This satisfies the canonical material-drift stop rule. The old line is superseded through:

```text
control/WORK_CLAIMS.json
handover/ETF_EU_PR80_TO_RELEASE_INTEGRATION_V3_20260809.md
```

## What is already resolved on current main

PR #78 was merged on 2026-08-08 as merge commit:

```text
994dbc8a6383b36510e981469d423c581ebc451b
```

That merged release integration established, among other things:

- the authoritative four-position funded model state;
- Alpha Vantage secret rotation and live provider reactivation;
- live 2026-08-05 funded pricing with 4/4 two-provider consensus;
- 4/4 exact-line identity anchors;
- zero historical-cache use for the funded current valuation;
- removal of inherited FX root assets and active FX workflow paths from the ETF EU product boundary;
- state-derived funded-universe pricing authority;
- convergence of the fresh-package route onto the WP11A pricing engine.

PR #82 was subsequently merged as:

```text
f4d814d31357c5d74b5dda079b21150687926929
```

It made the canonical non-delivery preview state-aware for the four-position portfolio and preserved:

```text
production_delivery_authority=false
send_executed=false
receipt_confirmed=false
```

The old `BLOCKED_EXTERNAL_CREDENTIAL` / `ROTATE_ALPHA_VANTAGE_REPOSITORY_SECRET` state is therefore retired and must not be resurrected by future sessions.

## Authoritative protected portfolio

Authority:

```text
output/etf_eu_portfolio_state.json
```

Current funded model positions:

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

This is the protected model state. A valuation/report run must preserve exact shares and cash unless a separate explicit allocation decision authorizes mutation.

## Current allocation authority

The PR #80 remediation established the still-relevant authority principle that must be reconstructed on the clean successor if absent from current `main`:

```text
explicit current allocation decision
> protected portfolio state and trade ledger
> current completed-close valuation
> donor opportunity state
> historical strategy context
```

The earlier proposed universal constraints are not current ETF EU authority:

```text
50% maximum position=RETIRED_UNSUPPORTED_SHADOW_RULE
35% minimum cash=RETIRED_UNSUPPORTED_SHADOW_RULE
15% maximum new ETF=RETIRED_UNSUPPORTED_SHADOW_RULE
75%=PRICING_COVERAGE_CONTEXT_NOT_POSITION_CAP
```

Any surviving client/report fragment that presents those unsupported fixed percentages as current allocation controls must fail closed.

## Independent assurance diagnosis that remains open

Issue #81 independently reviewed frozen PR #80 head:

```text
d38e8bad3575542bc8e5781812c9cd669f975a3a
ETF_EU_PR80_RELEASE_CLOSEOUT_VERIFY=FAIL
```

The machine lineage, pricing, repository-boundary and visual-page integrity evidence were materially strong, but the client output contradicted authoritative state. The release-blocking defect class was stale legacy/shadow report composition:

1. Section 6 still stated three official positions;
2. Section 13 contained a correct active L0CK row and a second stale 0.00% L0CK row;
3. Section 14 still presented fixed 50% / 35% minimum cash / 15% maximum new ETF as current controls;
4. Section 15 correctly showed L0CK as a 934-share active holding, exposing the contradiction.

PR #80 later received a generic repair and deterministic regression coverage for this defect class, but the final PR #80 head never obtained exact-head release assurance. The old `FAIL` remains diagnostic evidence only and cannot authorize the clean successor.

## Successor release contract

The clean successor must preserve newer `main` behavior and port only still-relevant donor deltas. Its release candidate is valid only if the exact surviving head proves:

```text
product_boundary=PASS
allocation_lineage=PASS
protected_state_preserved=true
funded_position_count=4
funded_same_date_two_provider_consensus=4/4
funded_exact_line_identity_anchors=4/4
historical_cache_required_for_current_funded_valuation=false
pricing_replay_contract=PASS
client_surface_supersession=PASS
no_duplicate_funded_ticker_state=true
no_stale_three_position_copy=true
no_retired_50_35_15_shadow_policy_as_current_control=true
nl_en_report_machine_validation=PASS
nl_en_report_visual_validation=PASS
fresh_independent_release_assurance=PASS
```

## Authority boundary

No report delivery is authorized or claimed in this reconciliation. No portfolio or ledger mutation occurred. No real broker execution occurred. Historical PR #80 generated artifacts and successful implementation runs are donor evidence only, not the current release candidate or a delivery receipt.