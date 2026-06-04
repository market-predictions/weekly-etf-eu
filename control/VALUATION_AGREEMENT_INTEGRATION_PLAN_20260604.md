# Valuation agreement integration plan — 2026-06-04

## Current decision

Add agreement-gate evidence to UCITS valuation artifacts, but do not let that evidence promote any row to `valuation_grade` yet.

## Reason

`config/ucits_pricing_source_policy.yml` currently contains a temporary Yahoo fallback posture, while the newer source metadata and agreement gate treat Yahoo as non-market-close agreement evidence. The safe bridge is to surface the agreement-gate result as evidence only.

## Intended artifact addition

Each valuation row should gain:

```text
agreement_gate_evidence
```

The row must still keep:

```text
valuation_grade=false
pricing_source=null
source_authority=null
observed_date=null
close=null
currency=null
completed_session=false
portfolio_mutation=false
production_delivery=false
funding_authority=false
```

## Intended blocker behavior

If the agreement gate does not produce valuation-grade agreement, append:

```text
agreement_gate_no_valuation_grade_agreement
```

If the agreement gate does produce valuation-grade evidence under a future source mix, append:

```text
agreement_gate_evidence_not_promoted_by_valuation_artifact_policy
```

until the coordinator explicitly authorizes valuation-grade promotion.

## Intended implementation choices

Preferred small-step implementation:

1. Add helper `pricing/valuation_agreement_evidence.py`.
2. Add agreement-gate evidence into `pricing/build_ucits_valuation_prices.py` rows.
3. Extend `tools/validate_ucits_valuation_prices.py` to require the evidence block when present and still block promotion.
4. Add compact tests.

## Current branch state

The helper file has been committed on:

```text
valuation-agreement-integration
```

Direct writes for the builder/enrichment module were blocked by the GitHub tool safety layer, so this plan records the next safe patch boundary.

## Authority boundaries

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no workflow changes
no output artifact changes
no report renderer changes
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```
