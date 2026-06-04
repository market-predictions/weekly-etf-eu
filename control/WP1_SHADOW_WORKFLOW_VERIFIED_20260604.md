# WP1 shadow workflow verification — completed

Date: 2026-06-04

Work package:

```text
Work Package 1 — Shadow workflow stabilisation
```

## Verification result

The non-production pricing-surface shadow workflow passed end-to-end.

Workflow:

```text
.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml
```

Committed validation evidence:

```text
output/validation/etf_eu_pricing_surface_shadow_20260604_213059.json
```

Evidence commit:

```text
3a930955fdbc0f108d1488b88ce3a892ee999c3f
```

Evidence payload:

```text
schema_version=etf_eu_pricing_surface_shadow_validation_v1
run_id=20260604_213059
report_date=2026-06-04
status=passed
workflow=weekly-etf-eu-pricing-surface-shadow.yml
```

## Fix completed during WP1

The pricing-surface validator was refined so it still blocks real positive funding / authority claims, but allows explicit negated cash-only wording such as:

```text
Funded UCITS holdings: none
not a funded UCITS holding
```

Validator fix commit:

```text
97b17144285626d8e0fa8f75d5213f0d21ee74a8
```

Latest shadow queue trigger:

```text
2d1a91d583ac91a8e3f3eb213791bdd1cc357b89
```

## Authority boundaries preserved

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

## Roadmap state after WP1

Completed:

```text
shadow workflow verification
```

Next controlled work package:

```text
main workflow wrapper switch
```

The main workflow switch must remain non-delivery and must preserve all authority boundaries above.
