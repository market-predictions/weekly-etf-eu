# ETF-EU-WP15T premium visual and Dutch-first refinement build notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15T
legacy_work_package_id=WP15T
source_work_package=ETF-EU-WP15S
status=completed_after_premium_dutch_refinement_candidate_build_and_validation
refined_pdf_candidate_path=output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf
refined_pdf_candidate_builder=runtime/build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate.py
refinement_build_artifact=output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build_20260703_000000.json
refinement_validator=tools/validate_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build.py
refinement_tests=tests/test_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build.py
selected_next_package=ETF-EU-WP15U
```

## Current issue

WP15S accepted the WP15R candidate as a content-complete foundation, but found it too technical, visually dense and English-first for premium client-grade use.

## Root cause

The content was present, but it still read like a validation surface: long rows, raw control language, limited hierarchy and no evidence badges. The Dutch report must be the primary EU client surface.

## Recommended change implemented

WP15T creates a new review-only refined PDF candidate with:

- Dutch-first client language.
- Premium cockpit hierarchy.
- Cards and true table-like layout.
- Evidence badges for UCITS/KID/pricing/funding/proxy status.
- Sequential flow from decision to evidence to risk, limitations and governance.
- Reduced raw control labels in the PDF body.

## Four-layer separation

Decision framework:

```text
The PDF now starts with "Beslissing nu" and an action card/table that states cash stays funded, candidates remain review-only, and no funding authority exists.
```

Input/state contract:

```text
The PDF keeps UCITS/ISIN/KID/exchange-line evidence visible without claiming live pricing, valuation-grade evidence or portfolio mutation.
```

Output contract:

```text
The PDF is Dutch-first, card/table based and visibly lighter than WP15R, but it remains review-only and still needs visual review before any client-grade claim.
```

Operational runbook:

```text
Validate with tools/validate_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build.py and test with tests/test_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build.py.
```

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

WP15T creates a stronger PDF candidate, but does not claim final client-grade readiness. It still needs a separate visual review checkpoint.

## Recommended next package

```text
ETF-EU-WP15U — ETF EU cockpit PDF premium Dutch refinement visual review checkpoint, no delivery
```
