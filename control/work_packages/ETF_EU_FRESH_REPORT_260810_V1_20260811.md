# ETF EU Fresh Report 260810 V1

Date: 2026-08-11
Issue: #97
Branch: `agent/etf-eu-fresh-260810-v1`
Owner role: `implementation_operations`
Status: `READY_FOR_PR_ASSURANCE`

## Objective
Produce a genuinely current Weekly ETF EU candidate for completed close 2026-08-10, broaden opportunity discovery through the canonical donor→UCITS fundability bridge, independently assure the exact candidate, merge only after PASS, and deliver only through separately guarded controlled transport with receipt evidence.

## Acceptance criteria
1. Broad donor lane evidence is selected from `market-predictions/weekly-etf` with source report date <= 2026-08-10. **PASS**
2. Donor lanes are mapped through `config/ucits_benchmark_proxy_map.yml`; unresolved mapping stays fail-closed. **PASS**
3. All current funded positions pass v2 exact-report-date funded two-provider consensus. **PASS — 6/6 in final candidate**
4. Mapped nonfunded exact lines are priced/qualified where provider evidence exists so opportunity breadth is real rather than documentary. **PASS**
5. Any change to the model funded set requires a separate explicit current allocation decision before protected portfolio/ledger mutation; no position is added merely to increase count. **PASS — decision `ETF-EU-CURRENT-20260810_123000`**
6. NL/EN MD/HTML/PDF are generated from one normalized state and include current re-underwriting/discovery evidence. **PASS — semantic rerender run 31502986816**
7. Candidate branch is frozen and independently reviewed by `governance_release_assurance`. **PENDING PR freeze**
8. Merge only after PASS + unchanged head and then exact-main validation. **PENDING**
9. Delivery only through `send-weekly-etf-eu-controlled-transport.yml` with exact artifact hashes, independent PASS, approved main lineage and separate guarded-send authority. **PENDING**
10. Delivery is not claimed until transport plus receipt/attachment evidence is positive. **PENDING**

## Protected boundaries
- real broker execution = false
- ungoverned portfolio mutation = false
- ungoverned trade-ledger write = false
- U.S. donor execution/report leakage = false
- retired 50%/35%/15% controls remain non-authoritative
- 75% remains pricing coverage, not a position cap

## Initial state
Protected funded set at cycle start: VWCE 151, EUNA 1526, SXR8 10, L0CK 934; cash EUR 50,208.40.
Latest identified donor breadth artifact at start: `weekly-etf/output/lane_reviews/etf_lane_assessment_260807.json` (12 breadth buckets, discovery engine v5).

## Current candidate state

```text
report_date=2026-08-10
run_id=20260810_123000
funded_positions=6
VWCE=151
EUNA=1526
SXR8=10
L0CK=934
DFEN=207  # added this run
IQQQ=149  # added this run
cash_eur=28101.01
invested_market_value_eur=72637.72
nav_eur=100738.73
real_broker_execution=false
```

The two new model positions are not a ticker-count target. DFEN and IQQQ passed distinct-exposure, exact identity/KID, current donor thesis/implementation review and two-provider completed-close evidence. XMLC remained the water implementation alternative; CBUF/VVSM/ISAE and incompletely mapped lanes remained unfunded.

## Material defects found and repaired during this cycle

1. Broad donor discovery existed architecturally but was not wired into canonical production execution.
2. Allocation-candidate pricing could deadlock because second-source quota was reserved for already-funded lines.
3. Alpha Vantage secret was not passed into the fresh pricing workflow.
4. SXR8/CSPX shared-ISIN validation incorrectly collapsed distinct trading lines; exact `(ISIN,ticker)` identity is now enforced.
5. Donor `is_fundable_candidate` contained U.S.-portfolio context and could not be used as EU funding authority; EU-local ranking/fundability now owns that decision.
6. Protected shares/cash and run-scoped valuation were mixed; current close revaluation now precedes allocation sizing.
7. Normalized report state lost current allocation-decision lineage and cash classification; the v2 state contract now preserves it.
8. Markdown, HTML and PDF could diverge semantically because legacy renderer copy was finalized before current decision semantics; `runtime/finalize_etf_eu_client_surface_semantics.py` now finalizes HTML before PDF rendering, while Markdown has its own fail-closed finalizer.
9. Dutch output could retain English donor fragments; language-specific finalization and regression checks now reject that leakage.

## Validation evidence

- final semantic rerender Actions run: `31502986816` — **SUCCESS**
- six-position applied-state assertion: PASS
- broad-discovery/semantic regressions: PASS
- package build: PASS
- cash/allocation normalized-state assertions: PASS
- strict NL/EN client-grade HTML/PDF validation: PASS
- strict NL/EN Markdown delivery validation: PASS
- explicit fresh-change/6-of-6 pricing semantics: PASS
- PDF review-page generation: PASS
- candidate branch persist: PASS
- temporary rerender workflow removed before assurance
- temporary push trigger removed from canonical candidate workflow; broad donor discovery + quota-aware EU pricing wiring retained
- delivery authority remains false

## Execution phases
A. request + discovery wiring — **COMPLETE**
B. current pricing + fundability evidence — **COMPLETE**
C. current allocation/re-underwriting decision — **COMPLETE**
D. six-artifact candidate generation + machine QA — **COMPLETE**
E. independent assurance — **NEXT**
F. merge + exact-main validation — **PENDING**
G. guarded delivery + receipt confirmation — **PENDING**
H. lifecycle/control closeout — **PENDING**
