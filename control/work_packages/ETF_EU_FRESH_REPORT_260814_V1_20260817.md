# ETF EU Fresh Report 260814 V1

## Identity

```text
workpackage_id=ETF-EU-FRESH-REPORT-260814-V1
issue=100
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-fresh-260814-v1
base_main_sha=427fb2e7213d997b571e0c55371086fbddd598ce
report_date=2026-08-14
run_id=20260814_235900
owner_role=implementation_operations
principal_decision_required=false
```

## Current issue
The predecessor 2026-08-10 report lineage was merged through PR #98 on 2026-08-15, but project-local state and claim records remained pre-merge and no successor production request was durably materialized. The successor branch existed at the merge SHA without executable work.

## Root cause
The lifecycle transition from assured/merged candidate to the next fresh production cycle was incomplete across three separate layers: project claim/state, executable routine request, and Control project intake. Chat intent and a branch alone are not execution authority.

## Decision framework
Run a genuinely fresh full weekly re-underwrite for completed close 2026-08-14. The six-position 2026-08-10 portfolio is prior authoritative model state, not a position-count target and not current-price truth. Donor discovery is research input; EU-local UCITS mapping/fundability and current exact-line pricing govern fundability. No retired 50%/35%/15% limits are reintroduced.

## Input/state contract
- predecessor routine manifest: `output/run_manifests/etf_eu_routine_run_manifest_2026-08-10_20260810_123000.json`;
- predecessor confirmed delivery closeout: `output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json`;
- canonical branch starts from exact merged main SHA `427fb2e7213d997b571e0c55371086fbddd598ce`;
- current completed-close evidence must be generated for report date 2026-08-14;
- funded exact lines require the existing two-provider consensus gate;
- portfolio/share/cash change requires an explicit current allocation decision artifact;
- real broker execution remains false.

## Output contract
Produce normalized Dutch and English Markdown, HTML and PDF from one current state. Pass strict semantic, portfolio, pricing, product-boundary and visual/PDF gates. Candidate generation has no delivery authority. Delivery success may only be recorded from positive guarded-transport plus receipt/attachment evidence.

## Operational runbook
1. Reconcile predecessor claim as `SUPERSEDED` with `report_delivery=false` and link this successor.
2. Repair `latest_etf_eu_routine_run_manifest_path.txt` to the real 2026-08-10 manifest.
3. Validate and execute request `control/run_queue/etf_eu_routine_report_request_20260814_235900.json` through `.github/workflows/run-weekly-etf-eu-routine.yml` on this non-main branch.
4. Run broad discovery -> EU mapping/fundability -> quota-aware pricing -> current revaluation -> full allocation re-underwrite -> NL/EN render.
5. Persist candidate artifacts and deterministic/visual evidence.
6. Open PR to `main`, freeze exact head and request independent `governance_release_assurance`.
7. Repair on FAIL; merge only unchanged PASSed head and exact-main validate.
8. Build hash-bound delivery package and use only the guarded delivery workflow.
9. Verify positive receipt/attachment evidence before claiming delivery.
10. Close issue/work package/claim and reconcile project + Control state.

## Acceptance criteria
- stale predecessor lifecycle is repaired without falsely claiming delivery;
- valid fresh request exists and binds real predecessor artifacts;
- durable Control intake exists for implementation;
- candidate run reaches PASS or records a concrete blocker;
- client-grade bilingual package is coherent;
- independent assurance is exact-head and fresh;
- no broker execution;
- delivery claim requires real receipt evidence;
- future cycle cannot silently idle merely because a chat request was not converted to durable work.
