# ETF-EU-WP15Q client-grade content completeness plan notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15Q
legacy_work_package_id=WP15Q
source_work_package=ETF-EU-WP15P
status=completed_after_content_completeness_contract_validation
content_contract_path=control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md
content_plan_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_content_completeness_plan_20260703_000000.json
content_plan_validator=tools/validate_etf_eu_cockpit_pdf_client_grade_content_completeness_plan.py
content_plan_tests=tests/test_etf_eu_cockpit_pdf_client_grade_content_completeness_plan.py
selected_next_package=ETF-EU-WP15R
```

## Current issue

WP15P confirmed that the WP15O premium cockpit PDF is visually improved, but still a review-only cockpit shell. It is not yet a content-complete client report surface.

## Root cause

The PDF surface currently proves visual hierarchy and governance markers, but not the actual client-grade ETF review content contract. It does not yet require holdings, allocation, UCITS investability, pricing/freshness evidence, decision tables, watchlist/candidate status, risk context, proxy disclosure, unresolved-data disclosure, or quality gates.

## Recommended change

Adopt `control/ETF_EU_COCKPIT_PDF_CLIENT_GRADE_CONTENT_CONTRACT_V1.md` as the minimum content-completeness contract before any delivery-preflight discussion can be reopened.

The next build package should create a review-only content-complete cockpit PDF candidate against this contract.

## Four-layer separation

Decision framework:

```text
The cockpit must answer which Dutch/EU-investable UCITS ETFs deserve capital, review, reduction, replacement, or no action.
```

Input/state contract:

```text
Every funded or investable ETF row must be ISIN-first, UCITS-first, KID-aware, exchange-line-specific, and pricing-source/freshness disclosed.
```

Output contract:

```text
The cockpit PDF must include executive read, holdings/cash, allocation, UCITS investability, pricing/freshness, decision table, watchlist, risk context, proxy disclosure, unresolved-data block, and governance footer.
```

Operational runbook:

```text
Validate the content completeness contract and artifact before allowing a later content-complete PDF build package. Do not enable delivery or live outbound paths.
```

## Required content sections

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
new_pdf_created=false
renderer_changed=false
source_pdf_replaced=false
```

## Recommended next package

```text
ETF-EU-WP15R — ETF EU cockpit PDF content-complete candidate build, no delivery
```

Purpose:

```text
Build a review-only content-complete ETF EU cockpit PDF candidate against the WP15Q content contract, without delivery, live data fetch, valuation-grade authority, funding authority, candidate promotion, or portfolio mutation.
```
