# ETF-EU-WP15R content-complete cockpit PDF candidate build notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15R
legacy_work_package_id=WP15R
source_work_package=ETF-EU-WP15Q
status=completed_after_content_complete_candidate_build_and_validation
content_contract_path=control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md
content_complete_pdf_candidate_path=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf
content_complete_pdf_candidate_builder=runtime/build_etf_eu_cockpit_pdf_content_complete_candidate.py
content_complete_candidate_build_artifact=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_build_20260703_000000.json
content_complete_candidate_validator=tools/validate_etf_eu_cockpit_pdf_content_complete_candidate_build.py
content_complete_candidate_tests=tests/test_etf_eu_cockpit_pdf_content_complete_candidate_build.py
selected_next_package=ETF-EU-WP15S
```

## Current issue

WP15Q defined the minimum client-grade content contract, but no content-complete cockpit PDF candidate existed yet.

## Root cause

The prior WP15O/WP15P PDF candidate proved visual hierarchy and governance markers, but did not include the full required client-facing content surface: holdings/cash, allocation, UCITS investability, pricing/freshness, decision table, watchlist/candidate status, risk context, proxy disclosure, unresolved-data block and governance footer.

## Recommended change implemented

WP15R creates a new review-only, content-complete cockpit PDF candidate at:

```text
output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf
```

The candidate is built against:

```text
control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md
```

## Four-layer separation

Decision framework:

```text
The candidate includes a weekly decision summary, holding-level action labels, cash posture, candidate review status and explicit no-funding/no-promotion markers.
```

Input/state contract:

```text
The candidate uses registry-derived static UCITS context only. It includes ISIN-first candidate identity, UCITS/KID status where known, exchange-line fields, pricing/freshness placeholders and unresolved evidence markers.
```

Output contract:

```text
The PDF includes all 12 required visible sections from the WP15Q content contract.
```

Operational runbook:

```text
Validate with tools/validate_etf_eu_cockpit_pdf_content_complete_candidate_build.py and test with tests/test_etf_eu_cockpit_pdf_content_complete_candidate_build.py.
```

## Content-complete sections included

1. Cockpit header with report date and authority markers.
2. Executive read and action summary.
3. Portfolio holdings and cash snapshot.
4. Allocation and concentration summary.
5. UCITS investability table.
6. Pricing and freshness evidence table.
7. Holding-level decision table.
8. Watchlist and candidate pipeline with promotion status.
9. Risk, regime and event context.
10. Proxy and benchmark disclosure.
11. Unresolved-data and limitation block.
12. Validation and governance footer.

## Boundary confirmation

```text
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
delivery_preflight_allowed=false
outbound_path_enabled=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
```

## Important limitation

The candidate is content-complete but still **not client-grade delivery**. It is a review-only PDF candidate. It does not perform live pricing, does not refresh macro or event context, does not create a valuation surface, does not mutate the portfolio, and does not authorize delivery preflight.

## Recommended next package

```text
ETF-EU-WP15S — ETF EU cockpit PDF content-complete candidate visual review checkpoint, no delivery
```
