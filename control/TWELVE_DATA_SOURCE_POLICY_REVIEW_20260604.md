# Twelve Data source policy review note

Date: 2026-06-04

Work package: Work Package 7 — Official/premium pricing source path

## Decision

Outcome B — allow Twelve Data as paid provider evidence, not agreement-gate authority.

This decision means Twelve Data may be treated as paid provider evidence after explicit provider-plan review and adapter config gating. It does not count for agreement-gate evidence and it is not valuation-grade eligible by default.

## Status

```text
adapter_path_implemented=true
focused_adapter_validation=passed
source_policy_decision=outcome_b_paid_provider_evidence_only
workflow_integrated=false
agreement_gate_authority=false
valuation_authority_integrated=false
```

## Rationale

Official Twelve Data terms define Internal Use as internal business use and define Redistribution as publication, distribution, or provision of Data to third parties. The terms grant access, receipt, processing, and storage of Data for Internal Use or as otherwise permitted by subscription tier or add-ons. External display or redistribution requires explicit authorization by a redistribution add-on or separate written agreement.

The Individual pricing page describes Individual use as personal, internal, and non-commercial. It also shows that higher paid tiers can include internal display or internal non-display access and ETF/global equity coverage, but this is not enough to approve third-party redistribution or client delivery without a business/commercial plan and redistribution review.

## Practical policy result

Twelve Data can be a paid-provider evidence path for controlled internal/source-policy-reviewed evidence.

Twelve Data cannot yet be:

```text
agreement_gate_evidence_source=true
valuation_grade_eligible=true
funding_authority=true
portfolio_mutation=true
production_delivery=true
candidate_promotion=true
```

## Required guardrails

The adapter remains gated by:

```text
paid_source_policy_reviewed=true
```

The adapter must keep stored lineage evidence free of provider tokens.

Required lineage flags remain:

```text
valuation_grade_by_adapter=false
portfolio_mutation=false
production_delivery=false
funding_authority=false
```

## Future integration conditions

Before any stronger role, a later decision must verify:

```text
business or commercial subscription scope
redistribution and external display rights
report/PDF/email artifact rights
attribution requirements
UCITS symbol mapping at ISIN plus venue level
currency/date/session quality
second independent source requirements
agreement-gate role
valuation-grade eligibility conditions
```

## Current implementation evidence

```text
pricing/sources/twelve_data.py
tests/test_twelve_data_adapter.py
tests/fixtures/pricing/twelve_data/resolved_time_series.json
tests/fixtures/pricing/twelve_data/provider_error.json
```

Focused validation:

```text
python -m pytest tests/test_twelve_data_adapter.py -q
3 passed
```

## Files intentionally not changed by this decision

```text
.github/workflows/send-weekly-etf-eu-report.yml
runtime/render_etf_eu_report_with_pricing_surface.py
output/etf_eu_portfolio_state.json
```

Twelve Data is not wired into the main workflow by this review note.
