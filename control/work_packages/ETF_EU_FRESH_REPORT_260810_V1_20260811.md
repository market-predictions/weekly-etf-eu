# ETF EU Fresh Report 260810 V1

Date: 2026-08-11
Issue: #97
Branch: `agent/etf-eu-fresh-260810-v1`
Owner role: `implementation_operations`
Status: `ACTIVE`

## Objective
Produce a genuinely current Weekly ETF EU candidate for completed close 2026-08-10, broaden opportunity discovery through the canonical donor→UCITS fundability bridge, independently assure the exact candidate, merge only after PASS, and deliver only through separately guarded controlled transport with receipt evidence.

## Acceptance criteria
1. Broad donor lane evidence is selected from `market-predictions/weekly-etf` with source report date <= 2026-08-10.
2. Donor lanes are mapped through `config/ucits_benchmark_proxy_map.yml`; unresolved mapping stays fail-closed.
3. All current funded positions pass v2 exact-report-date funded two-provider consensus.
4. Mapped nonfunded exact lines are priced/qualified where provider evidence exists so opportunity breadth is real rather than documentary.
5. Any change to the model funded set requires a separate explicit current allocation decision before protected portfolio/ledger mutation; no position is added merely to increase count.
6. NL/EN MD/HTML/PDF are generated from one normalized state and include current re-underwriting/discovery evidence.
7. Candidate branch is frozen and independently reviewed by `governance_release_assurance`.
8. Merge only after PASS + unchanged head and then exact-main validation.
9. Delivery only through `send-weekly-etf-eu-controlled-transport.yml` with exact artifact hashes, independent PASS, approved main lineage and separate guarded-send authority.
10. Delivery is not claimed until transport plus receipt/attachment evidence is positive.

## Protected boundaries
- real broker execution = false
- ungoverned portfolio mutation = false
- ungoverned trade-ledger write = false
- U.S. donor execution/report leakage = false
- retired 50%/35%/15% controls remain non-authoritative
- 75% remains pricing coverage, not a position cap

## Initial state
Protected funded set: VWCE 151, EUNA 1526, SXR8 10, L0CK 934; cash EUR 50,208.40.
Latest identified donor breadth artifact at start: `weekly-etf/output/lane_reviews/etf_lane_assessment_260807.json` (12 breadth buckets, discovery engine v5).

## Execution phases
A. request + discovery wiring
B. current pricing + fundability evidence
C. current allocation/re-underwriting decision
D. six-artifact candidate generation + machine QA
E. independent assurance
F. merge + exact-main validation
G. guarded delivery + receipt confirmation
H. lifecycle/control closeout
