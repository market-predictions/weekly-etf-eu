# ETF EU PR #80 → Release Integration V3 Handover

```text
handover_id=ETF-EU-HO-PR80-TO-INTEGRATION-V3-20260809
claim_id=ETF-EU-PR80-RELEASE-REMEDIATION
from_owner_or_role=implementation_operations
to_owner_or_role=implementation_operations
coordinator=portfolio_control
repository=market-predictions/weekly-etf-eu
source_branch=agent/etf-eu-client-grade-release-remediation
exact_source_head_sha=01fb4e9238d1921dc8fd52ad552d3acba5bfceea
exact_target_or_main_sha=93dbe7450e44d22a2fe247a8d1f1ffb9e07adf3c
successor_claim_id=ETF-EU-RELEASE-INTEGRATION-V3
successor_branch=agent/etf-eu-release-integration-v3
disposition=SUPERSEDE
created_at=2026-08-09T21:20:00Z
```

## Why this handover exists

PR #80 is no longer a valid integration line. Live comparison against `main` at reconciliation showed:

```text
status=diverged
ahead_by=95
behind_by=147
merge_base=050bf08506b54400615538feeca272fbf967ed82
```

This meets the canonical material-drift stop condition in `market-predictions/control-plane/control/WORK_CLAIM_AND_BRANCH_LIFECYCLE_STANDARD_V1.md`.

The old branch is therefore frozen as read-only implementation and evidence donor material. It must not receive further product, remediation, generated client-output, release-candidate or CI-retrigger commits intended to advance release readiness.

## Scope completed on the superseded lineage

The PR #80 lineage established or materially advanced these areas:

- separation of Weekly ETF EU product execution from inherited Weekly FX execution paths;
- explicit ETF EU release/allocation authority hierarchy and protected-state lineage;
- removal of unsupported universal 50% position, 35% minimum-cash and 15% maximum-new-ETF shadow constraints;
- four-position model-state awareness including L0CK;
- multi-provider completed-close pricing and replay-safe pricing evidence;
- current-package/release-manifest lineage controls;
- regression coverage for activated portfolio copy;
- independent-assurance diagnosis of stale client-facing fragments;
- generic repair for stale three-position copy, duplicate funded L0CK action rows and retired shadow allocation controls;
- regression tests that fail closed when authoritative funded-row identity cannot be established.

These are donor results, not blanket authorization to copy all 95 branch commits or generated artifacts.

## Evidence retained from the superseded lineage

Important historical evidence includes:

- PR #80 itself and its exact head `01fb4e9238d1921dc8fd52ad552d3acba5bfceea`;
- successful fresh-package/pricing runs on earlier exact PR #80 heads, including run `31262475314`;
- persisted 2026-08-07 NL/EN candidate artifacts as historical implementation evidence only;
- independent assurance issue #81 `FAIL` on frozen head `d38e8bad3575542bc8e5781812c9cd669f975a3a`;
- subsequent generic client-surface repair beginning with commit `707058bde97febbd8e860016c6bd58356b2bb9d2` and its regression/CI follow-ups.

The prior assurance `FAIL` is diagnostic evidence only and can never authorize a repaired descendant or successor candidate.

## Unresolved items transferred to the successor

`ETF-EU-RELEASE-INTEGRATION-V3` owns the remaining current-release work:

1. reconstruct only the still-relevant PR #80 delta on top of current `main`;
2. preserve newer `main` changes from merged work packages such as PR #78 and PR #82;
3. remove any inherited FX product-boundary material that still exists on current `main`;
4. preserve the protected four-position model portfolio and allocation authority contract;
5. port the generic stale-client-fragment repair and required regression coverage where absent from current `main`;
6. run the complete exact-head product-boundary, allocation-lineage, pricing/replay, client-surface and report-validation gates;
7. generate a fresh Dutch-primary / English-companion four-file candidate from the surviving exact head;
8. machine- and visually validate the new candidate, with explicit checks on sections 6, 13, 14 and 15;
9. obtain a fresh independent `governance_release_assurance` decision for that exact candidate;
10. only after a valid PASS may the successor be considered for merge/release progression.

## Authority boundaries

This handover does not authorize:

- real broker execution;
- a portfolio or ledger mutation;
- report transport or email delivery;
- reuse of prior candidate hashes as current authority;
- weakening the two-provider or exact-line identity gates;
- treating historical PR #80 generated outputs as the current release candidate.

## Next action

Continue exclusively on `agent/etf-eu-release-integration-v3` after the lifecycle/control reconciliation is merged to `main`. The superseded PR #80 branch remains available only for minimum-delta reconstruction and historical evidence retrieval.
