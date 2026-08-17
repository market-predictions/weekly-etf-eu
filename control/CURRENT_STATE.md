# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-17
repository=market-predictions/weekly-etf-eu
state=FRESH_20260814_PRODUCTION_MATERIALIZED
parent_issue=100
branch=agent/etf-eu-fresh-260814-v1
base_main_sha=427fb2e7213d997b571e0c55371086fbddd598ce
run_id=20260814_235900
report_date=2026-08-14
active_release_integration_claim=ETF-EU-FRESH-REPORT-260814-V1
principal_decision_required=false
delivery_authorized=false
real_broker_execution=false
report_delivery=false
smtp_send=false
```

## Live reconciliation
PR #98, the fresh 2026-08-10 six-position candidate, received independent exact-head PASS in issue #99 and was merged unchanged on 2026-08-15. Current merged main/base for this successor cycle is `427fb2e7213d997b571e0c55371086fbddd598ce`.

The predecessor 2026-08-10 report was **not delivered**. Its candidate/merge evidence remains historical strategy and model-state provenance only. Delivery authority and delivery receipt were never established for that lineage.

The prior project control files incorrectly remained at the pre-merge `READY_FOR_ASSURANCE` state after PR #98 merged. In addition, branch `agent/etf-eu-fresh-260814-v1` existed at the merged base without a durable production request. Those stale lifecycle defects are repaired under issue #100.

## Predecessor model state entering the fresh cycle

| Ticker | Shares | Entering role |
|---|---:|---|
| VWCE | 151 | Global core equity |
| EUNA | 1,526 | Stabilising aggregate bonds |
| SXR8 | 10 | U.S. equity overweight |
| L0CK | 934 | Cybersecurity satellite |
| DFEN | 207 | Defense resilience satellite |
| IQQQ | 149 | Water infrastructure satellite |

```text
predecessor_cash_eur=28101.01
predecessor_invested_market_value_eur=72637.72
predecessor_nav_eur=100738.73
predecessor_position_count=6
predecessor_report_date=2026-08-10
real_broker_execution=false
```

These values are the authoritative predecessor model state. They are **not** current 2026-08-14 prices, not an instruction to retain six positions and not a position-count target. The 2026-08-14 cycle must revalue and re-underwrite the whole portfolio using fresh completed-close evidence.

## Fresh 2026-08-14 production contract

Work package:

`control/work_packages/ETF_EU_FRESH_REPORT_260814_V1_20260817.md`

Routine request:

`control/run_queue/etf_eu_routine_report_request_20260814_235900.json`

Control runtime intake:

`control-runtime-state:control/project-intake/WEEKLY_ETF_EU_100_FRESH_260814.json`

The request is explicitly bound to:

- previous routine manifest: `output/run_manifests/etf_eu_routine_run_manifest_2026-08-10_20260810_123000.json`;
- previous confirmed delivery closeout: `output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json`.

The stale helper pointer that still referenced 2026-07-12 has been repaired on this branch to the actual 2026-08-10 routine manifest.

## Decision framework retained

- full weekly portfolio re-underwrite; no ticker-count target;
- broad donor discovery is research input only;
- EU-local UCITS mapping/fundability owns funding eligibility;
- current exact trading-line pricing is distinct from historical report context;
- funded exact lines require the existing two-provider completed-close consensus gate;
- 50% maximum position, 35% minimum cash and 15% maximum new ETF remain retired as current authority;
- 75% remains pricing-coverage context only, not a position cap;
- 25% turnover / 18% semiconductor-theme values remain research/shadow unless separately adopted;
- any model share/cash mutation requires an explicit current allocation-decision artifact;
- real broker execution remains false.

## Output contract
The fresh cycle must derive Dutch and English Markdown, HTML and PDF from one normalized current state and pass deterministic semantic, pricing, portfolio, product-boundary and visual/PDF gates. Candidate generation has no delivery authority.

## Operational state

```text
issue_100=OPEN
workpackage=MATERIALIZED
routine_request=MATERIALIZED
branch=ACTIVE
control_intake=MATERIALIZED
control_queue=PENDING_MATERIALIZATION
candidate_run=PENDING
candidate_pr=PENDING
independent_assurance=PENDING
guarded_delivery=PENDING
receipt=PENDING
```

## Next lifecycle
1. Allow the canonical worker reconciliation to materialize task `WEEKLY_ETF_EU_100_FRESH_260814_IMPLEMENTATION` into `control/DISPATCH_QUEUE.json`; the current queue did not yet contain it immediately after intake creation.
2. The claimed `implementation_operations` worker executes `.github/workflows/run-weekly-etf-eu-routine.yml` against the non-main successor branch and exact request path.
3. Re-underwrite from current 2026-08-14 completed-close evidence; repair only genuine failures.
4. Persist and validate the bilingual client-grade candidate.
5. Open/freeze PR and obtain fresh independent exact-head `governance_release_assurance`.
6. Merge only unchanged PASSed head, exact-main validate, and enter separate guarded delivery.
7. Claim successful email delivery only after positive transport plus receipt/attachment evidence.
8. Close issue/work package/claim and reconcile project + Control state.
