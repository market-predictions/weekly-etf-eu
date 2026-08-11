# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-11
repository=market-predictions/weekly-etf-eu
state=DONOR_PARITY_RECONCILIATION_CLOSED
parent_issue=90
post_merge_repair_issue=94
assurance_issue=96
repair_pr=95
reviewed_head=e5d3470e1e1ab7f402a02cb31b775f3f902d4928
code_merge_sha=10823b7c457a253e409a768f52ee95b1522c363f
code_merge_tree=71a614575bdc1d675ece53684d14601ce76fde90
exact_main_product_boundary_run=31472717495
active_release_integration_claim=NONE
principal_decision_required=false
delivery_authorized=false
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
```

## Outcome
The donor-parity, allocation-authority, pricing-contract, bilingual-output, workflow-topology and post-merge US donor-leak reconciliation program is closed.

PR #91 first established the corrected decision/state/output/runbook architecture. Its independent issue #93 PASS was valid and PR #91 merged unchanged. Exact-main observation then exposed a separate legacy operational defect: retained US Weekly ETF donor pricing/report workflows could still execute inside Weekly ETF EU and one of them wrote US pricing artifacts to `main`.

Issue #94 / PR #95 repaired that post-merge defect. Independent issue #96 returned:

`ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS`

on exact frozen head `e5d3470e1e1ab7f402a02cb31b775f3f902d4928`. PR #95 then merged unchanged as `10823b7c457a253e409a768f52ee95b1522c363f`.

## Exact-main closeout evidence

Push run `31472717495` checked out exact merge SHA `10823b7c...` and returned:

```text
product_boundary=PASS
planted_boundary_tests=6 passed
active_workflows_scanned=32
blockers=[]
```

No retired donor workflow executed on the merge push. The two erroneous US pricing artifact paths remain absent.

The real merge and the assurance synthetic merge have the identical Git tree:

`71a614575bdc1d675ece53684d14601ce76fde90`

Therefore the frozen PR workflow-authority evidence applies to exact merged code content:

```text
active_workflows=32
retired_disabled=23
candidate_route=1
delivery_route=1
us_donor_execution_routes=0
```

## Current protected portfolio

| Ticker | Shares |
|---|---:|
| VWCE | 151 |
| EUNA | 1,526 |
| SXR8 | 10 |
| L0CK | 934 |

```text
cash_eur=50208.40
portfolio_blob=df710b5fbe4172506b67b7f591030a8c6a098c64
trade_ledger_blob=c6765ba380fe0c40272688a017dc0dc99b46d571
```

Protected state and ledger are unchanged.

## Stable authority retained

- 50% maximum position: retired as current authority;
- 35% minimum cash: retired as current authority;
- 15% maximum new ETF: retired as current authority;
- 75%: pricing-coverage context only, not a position cap;
- 25% turnover / 18% semiconductor-theme values: research/shadow only unless separately adopted;
- donor cash/factor thresholds: review/disclosure triggers, not allocation caps;
- model investability remains broker-neutral;
- missing current evidence remains unresolved rather than implicit Hold.

## Operational topology

- one non-main candidate route: `run-weekly-etf-eu-routine.yml`;
- one real guarded delivery route: `send-weekly-etf-eu-controlled-transport.yml`;
- 23 retired historical/legacy routes retained only as non-executable `.disabled` audit evidence;
- retained donor source/research logic does not imply donor operational authority.

## Claim and handover

Successor claim `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1` is `CLOSED`.

Closeout handover:

`handover/ETF_EU_POST_MERGE_US_DONOR_LEAK_REPAIR_V1_CLOSE_20260811.md`

There is no active release-integration claim left from this reconciliation program.

## Next lifecycle

A genuinely current Weekly ETF EU report is a **new separate production candidate cycle**. It must resolve the latest valid completed close, run current donor discovery → EU UCITS mapping/fundability → exact-line v2 pricing → current re-underwriting, generate NL/EN MD/HTML/PDF from one normalized state, obtain fresh independent report assurance, and use separately authorized guarded delivery if sending is requested.

This closeout itself creates no report-delivery or broker-execution authority.
