# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
EXECUTE_FRESH_20260814_PRODUCTION_CYCLE
```

Current authoritative execution identity:

```text
issue=100
branch=agent/etf-eu-fresh-260814-v1
base_main_sha=427fb2e7213d997b571e0c55371086fbddd598ce
run_id=20260814_235900
report_date=2026-08-14
active_claim=ETF-EU-FRESH-REPORT-260814-V1
workpackage=control/work_packages/ETF_EU_FRESH_REPORT_260814_V1_20260817.md
request=control/run_queue/etf_eu_routine_report_request_20260814_235900.json
delivery_authorized=false
real_broker_execution=false
principal_decision_required=false
```

## Reconciled predecessor — do not misstate

The 2026-08-10 candidate was independently PASSed in issue #99 and merged unchanged through PR #98 on 2026-08-15. Its predecessor model state is six funded positions with EUR 28,101.01 cash and NAV EUR 100,738.73 at the 2026-08-10 valuation.

That report lineage was **not delivered**. Do not rewrite merge as delivery and do not treat 2026-08-10 prices as current 2026-08-14 truth. The old claim is to be superseded by the current cycle, with delivery remaining false.

## Completed recovery work in issue #100

1. Reconciled live PR #98 merge/base identity.
2. Reused the already-created successor branch rather than creating a competing release line.
3. Created the fresh-cycle work package.
4. Created a schema-v2 fresh routine request for report date 2026-08-14.
5. Bound the request to the real 2026-08-10 predecessor routine manifest and the last confirmed delivery closeout.
6. Repaired the stale latest-routine pointer that incorrectly referenced 2026-07-12.
7. Replaced the stale pre-merge human-readable current-state narrative on the active successor branch.

## Immediate execution sequence

1. Reconcile `control/WORK_CLAIMS.json`: mark `ETF-EU-FRESH-REPORT-260810-V1` `SUPERSEDED`/undelivered and establish `ETF-EU-FRESH-REPORT-260814-V1` as the sole active current release-line claim.
2. Materialize explicit validated `PROJECT_INTAKE_V1` for issue #100 on Control `control-runtime-state` so work no longer depends on chat relay.
3. Execute the canonical `.github/workflows/run-weekly-etf-eu-routine.yml` on `agent/etf-eu-fresh-260814-v1` with request path `control/run_queue/etf_eu_routine_report_request_20260814_235900.json`.
4. Require fresh completed-close evidence for 2026-08-14. Do not fall back to historical/current-live mismatches.
5. Run broad discovery -> EU-local mapping/fundability -> exact-line pricing -> full current revaluation -> explicit allocation decision -> normalized bilingual render.
6. Repair genuine machine/client-surface failures without weakening gates.
7. Persist candidate artifacts; run deterministic and visual/PDF validation.
8. Open candidate PR to `main`; freeze exact head.
9. Obtain fresh independent `governance_release_assurance`. A previous PASS cannot authorize a changed 2026-08-14 candidate.
10. Merge only the exact unchanged PASSed head; run exact-main verification.
11. Build the hash-bound delivery package and invoke only the separately guarded controlled-transport route.
12. Verify transport + receipt/attachment evidence before stating that delivery succeeded.
13. Close issue #100, work package and claim; reconcile `CURRENT_STATE.md`, `NEXT_ACTIONS.md`, stable decision/defect history and Control cache.

## Protected boundaries

- no real broker execution;
- no share/cash mutation without explicit current allocation-decision authority;
- no hard position-count target;
- no retired 50%/35%/15% allocation limits;
- no research-only mapping/price becomes funding authority automatically;
- candidate generation has no SMTP/delivery authority;
- no delivery success claim without a real receipt/manifest.

## Autonomy invariant added by this recovery
A statement that no principal decision is required is insufficient unless the next executable step is also durably materialized. Every future transition that requires autonomous continuation must leave either an executable project intake/queue state, an active worker/run identity, or an explicit blocker with next owner/action. A branch, narrative next action or chat intention alone is not progress authority.
