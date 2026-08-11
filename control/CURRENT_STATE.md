# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-11
repository=market-predictions/weekly-etf-eu
state=FRESH_20260810_CANDIDATE_READY_FOR_ASSURANCE
parent_issue=97
branch=agent/etf-eu-fresh-260810-v1
run_id=20260810_123000
report_date=2026-08-10
active_release_integration_claim=ETF-EU-FRESH-REPORT-260810-V1
principal_decision_required=false
delivery_authorized=false
real_broker_execution=false
report_delivery=false
smtp_send=false
```

## Current outcome
A genuinely fresh Weekly ETF EU candidate has been produced for completed close 2026-08-10. The cycle uses broad donor discovery as research input, EU-local UCITS mapping/fundability, exact trading-line pricing and an explicit model-only allocation decision.

The candidate moved from four to six funded model positions because two distinct opportunities passed the current evidence gates. This was not a position-count target.

## Current model portfolio candidate

| Ticker | Shares | Current role |
|---|---:|---|
| VWCE | 151 | Global core equity |
| EUNA | 1,526 | Stabilising aggregate bonds |
| SXR8 | 10 | U.S. equity overweight |
| L0CK | 934 | Cybersecurity satellite |
| DFEN | 207 | Defense resilience satellite — added this run |
| IQQQ | 149 | Water infrastructure satellite — added this run |

```text
cash_eur=28101.01
invested_market_value_eur=72637.72
nav_eur=100738.73
position_count=6
real_broker_execution=false
```

Model activation authority is the explicit current decision:

`output/activation/etf_eu_current_allocation_decision_20260810_123000.json`

The decision funded DFEN and IQQQ from cash after EU-local re-underwriting and two-provider completed-close evidence. XMLC remains the water implementation alternative. CBUF, VVSM, ISAE and incompletely mapped lanes remain unfunded because their current evidence does not meet the same gate.

## Fresh discovery and pricing state

- donor breadth research: 12 required buckets / 25 assessed lanes;
- current pricing date: 2026-08-10;
- funded exact-line valuation: 6/6 two-provider completed-close consensus;
- nonfunded pricing remains research/comparison evidence and has no automatic funding authority;
- remaining cash is classified through deploy-or-explain logic, not a fixed 35% floor.

## Output-contract state
NL/EN Markdown, HTML and PDF now derive their current decision semantics from one normalized state.

The cycle repaired a P0 stale-output defect where legacy renderer copy could still say no portfolio change / zero verified lines despite the six-position state. The permanent v2 builder now applies a fail-closed client-surface semantics finalizer before HTML is persisted and before PDF rendering.

Final semantic rerender Actions run:

```text
run=31502986816
verdict=PASS
six_position_state=PASS
normalized_allocation_cash_state=PASS
strict_nl_en_html_pdf_validation=PASS
strict_nl_en_markdown_validation=PASS
fresh_change_and_6_of_6_semantics=PASS
pdf_review_pages=PASS
```

## Stable authority retained

- 50% maximum position: retired as current authority;
- 35% minimum cash: retired as current authority;
- 15% maximum new ETF: retired as current authority;
- 75%: pricing-coverage context only, not a position cap;
- 25% turnover / 18% semiconductor-theme values: research/shadow only unless separately adopted;
- donor U.S.-portfolio funding labels are not EU funding authority;
- model investability remains broker-neutral;
- exact trading line remains distinct even where ISIN is shared across venues/tickers;
- missing current evidence remains unresolved rather than implicit Hold.

## Operational topology at assurance boundary

- one canonical non-main candidate route: `.github/workflows/run-weekly-etf-eu-routine.yml`;
- broad donor discovery and quota-aware allocation-candidate pricing are integrated in that route;
- the issue-#97 push trigger has been removed;
- the temporary rerender workflow has been removed;
- one guarded delivery route remains separate: `send-weekly-etf-eu-controlled-transport.yml`;
- candidate generation has no delivery authority.

## Claim and lifecycle

Active claim:

`ETF-EU-FRESH-REPORT-260810-V1`

Work package:

`control/work_packages/ETF_EU_FRESH_REPORT_260810_V1_20260811.md`

Issue: `#97`.

## Next lifecycle

1. open the fresh candidate PR against `main`;
2. validate exact PR head and freeze it;
3. obtain independent `governance_release_assurance` verdict;
4. merge only on PASS with unchanged head;
5. run exact-main verification;
6. build/validate the delivery package against the assured main lineage;
7. use the sole guarded transport route;
8. claim successful delivery only after positive receipt/attachment evidence;
9. close claim/work package and reconcile control state.
