# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
RECONSTRUCT_ONE_CLEAN_RELEASE_LINE_FROM_CURRENT_MAIN
```

Current authoritative work lineage:

```text
work_package=ETF-EU-WP-RELEASE-INTEGRATION-V3
active_claim=ETF-EU-RELEASE-INTEGRATION-V3
branch=agent/etf-eu-release-integration-v3
target=main
superseded_pr=80
principal_decision_required=false
principal_action_required=false
```

The former PR #78 / Alpha Vantage rotation sequence is complete and obsolete. Do not reopen it.

## Immediate sequence

1. Merge the work-claim/branch lifecycle reconciliation so `main` records one active integration claim and the explicit PR #80 → V3 supersession handover.
2. Fast-forward the still-clean `agent/etf-eu-release-integration-v3` branch to the resulting current `main` so the successor begins on one exact contemporary base.
3. Compare current `main` against PR #80 path-by-path and classify every PR #80 change as one of:
   - already present on current `main`;
   - still relevant and must be ported;
   - superseded by newer `main` behavior;
   - historical/generated evidence only and must not be ported.
4. Port only the minimum still-relevant source/config/test/workflow deltas. Do not cherry-pick or force-merge the 95-commit PR #80 history.
5. Specifically prove or restore, where needed:
   - product-boundary separation from inherited FX execution;
   - `ETF_EU_RELEASE_LINEAGE_POLICY_V2` allocation authority semantics;
   - protected four-position valuation-only state preservation;
   - replay-safe/multi-provider completed-close pricing contracts;
   - generic client-surface supersession repair;
   - deterministic rejection of stale three-position copy, duplicate funded ticker rows and retired fixed 50%/35%/15% shadow controls.
6. Open one successor release-integration PR and update `control/WORK_CLAIMS.json` with its PR identity at the next reconciliation gate.
7. Run all relevant exact-head CI on that successor, including product-boundary, allocation-lineage, pricing/replay, activated-client-surface and final report-validation gates.
8. Generate a fresh Dutch-primary / English-companion four-file candidate only after the exact source head is green.
9. Validate the fresh NL/EN HTML and PDF artifacts mechanically and visually. Explicitly inspect Sections 6, 13, 14 and 15 for the defect class found by issue #81.
10. Obtain a fresh independent `governance_release_assurance` verdict bound to the exact successor candidate. Prior PR #80 `FAIL` evidence is diagnostic only.
11. If assurance returns PASS, merge the successor and close PR #80 as superseded, preserving its handover/evidence pointers. If assurance returns FAIL/INDETERMINATE, repair through a new exact candidate and re-assure.
12. Reconcile `control/CURRENT_STATE.md`, this file, `control/WORK_CLAIMS.json`, relevant work-package records and portfolio-control state onto the surviving merged lineage.
13. Only after a separately authorized guarded-delivery step may transport be considered. Delivery success requires independent receipt/attachment evidence; generation, CI and SMTP invocation are insufficient.

## Already completed and not to be repeated

```text
PR78_merged=true
alpha_vantage_secret_rotation_complete=true
funded_live_consensus_2026_08_05=4/4
funded_identity_anchors_2026_08_05=4/4
historical_cache_used_for_that_funded_run=0
funded_position_count=4
PR82_four_position_preview_repair_merged=true
PR80_material_drift_diagnosed=true
PR80_status=SUPERSEDED_DONOR_LINEAGE
clean_successor_branch_created=true
```

## PR #80 donor evidence to preserve, not blindly merge

Important donor evidence includes:

```text
pr80_head=01fb4e9238d1921dc8fd52ad552d3acba5bfceea
historical_assurance_head=d38e8bad3575542bc8e5781812c9cd669f975a3a
historical_assurance_verdict=FAIL
fresh_package_run=31262475314
client_surface_generic_repair_commit=707058bde97febbd8e860016c6bd58356b2bb9d2
```

The old branch may be read for code and evidence but may not receive new release-advancing commits.

## Prohibited shortcuts

Do not:

- continue remediation or CI-retrigger accumulation on PR #80;
- force-merge or wholesale rebase the 95-commit donor lineage into current `main`;
- port generated historical report/evidence artifacts merely because they exist in PR #80;
- weaken the funded two-provider same-date requirement or exact-line identity requirements;
- mutate shares or cash during valuation/report reconstruction without explicit allocation authority;
- reintroduce unsupported universal 50% maximum-position, 35% minimum-cash or 15% maximum-new-ETF controls;
- treat the donor's 75% pricing-coverage context as a position-weight cap;
- reuse the prior independent FAIL as approval for a descendant or successor;
- send email, claim delivery, imply broker execution or claim production closeout from a successful candidate build alone.