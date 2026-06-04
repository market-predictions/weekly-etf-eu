# Valuation agreement integration plan — 2026-06-04

## Current decision

Add agreement-gate evidence to UCITS valuation artifacts, but do not let that evidence promote any row to `valuation_grade` yet.

## Reason

`config/ucits_pricing_source_policy.yml` currently contains a temporary Yahoo fallback posture, while the newer source metadata and agreement gate treat Yahoo as non-market-close agreement evidence. The safe bridge is to surface the agreement-gate result as evidence only.

## Implemented in this branch

```text
pricing/valuation_agreement_evidence.py
pricing/enrich_ucits_valuation_agreement.py
tests/test_valuation_agreement_evidence.py
```

The implemented helper and enrichment module can attach:

```text
agreement_gate_evidence
```

to valuation artifact rows while preserving:

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

## Builder wiring still pending

The intended final patch to `pricing/build_ucits_valuation_prices.py` is:

```text
artifact = enrich_valuation_artifact(build_valuation_artifact(...))
```

inside `write_valuation_artifact()` before the artifact is written.

This full-file update has been blocked repeatedly by the GitHub tool safety layer, even when the requested change was minimal and non-destructive.

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

## Current PR status

PR #10 is a draft bridge PR. It is useful as the tested bridge layer, but it should not be marked complete until `pricing/build_ucits_valuation_prices.py` is wired or a coordinator explicitly chooses the CLI enrichment path as the interim integration pattern.

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
