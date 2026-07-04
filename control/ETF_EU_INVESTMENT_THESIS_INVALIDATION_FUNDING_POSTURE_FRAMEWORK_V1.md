# ETF EU investment thesis, invalidation criteria, and funding posture framework v1

## Purpose

Define a deterministic review-only decision framework for investment thesis, invalidation criteria, and funding posture in the ETF EU review workflow.

## Scope

This framework applies to the committed review-only evidence chain through ETF-EU-WP15AI. It supports structured analysis for IE00B5BMR087 and the successful SXR8.DE and CSPX.L trading lines. It does not create operational authority.

## Authority boundary

```text
review_only=true
investment_thesis_framework_created=true
invalidation_criteria_framework_created=true
funding_posture_framework_created=true
decision_framework_validated=true
client_grade_claim=false
delivery_preflight_allowed=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
live_price_fetch_performed=false
pricing_evidence_changed=false
new_pdf_created=false
renderer_changed=false
```

## Review-only thesis framework

A review-only thesis may explain why a broad, physically replicated, accumulating S&P 500 UCITS ETF could be a candidate exposure in a future EU client report, subject to remaining gates. The thesis must remain conditional on evidence quality, client language quality, source authority, and explicit future authority.

A thesis framework is not a transaction recommendation.

## Evidence dependency rules

The framework must depend on committed evidence only:

```text
product facts evidence from WP15AG
pricing freshness and valuation policy from WP15AH
PRIIPs/KID and liquidity/spread investability evidence from WP15AI
ISIN-first registry evidence
review-only pricing artifacts
```

No newer price, spread, valuation, or portfolio state may be inferred.

## Invalidation criteria framework

Invalidation criteria are review-only guardrails, not live trading triggers. Criteria must block promotion when source authority, pricing freshness, liquidity/spread, product facts, client language, funding authority, or delivery-preflight evidence is insufficient.

## Funding posture framework

Funding posture is framework-only. It may identify future preconditions before any funding discussion can occur, but it does not set cash posture, position size, allocation, portfolio weight, execution instruction, or funded status.

A funding posture framework is not a cash allocation.

## Candidate-not-funded rule

All candidates remain not funded unless a later package explicitly receives funding authority and portfolio mutation authority. WP15AJ creates neither.

## What this framework does not authorize

This framework does not create funded positions.

This framework does not create funding authority.

This framework does not mutate portfolio state.

This framework does not create valuation-grade authority.

This framework does not create client-grade authority.

This framework does not enable delivery-preflight.

This framework does not change recommendation logic in production.

This framework does not create cash allocation, target weights, position sizes, trade signals, execution instructions, report delivery, delivery receipts, or production manifests.

## Remaining client-grade blocker

After this framework is defined, the remaining client-grade blocker must still include:

```text
client_language_quality_gate
```

## Delivery-preflight limitation

Delivery-preflight remains blocked until all client-grade gates pass and delivery authority, recipient authority, transport authority, receipt/manifest contract, outbound runbook, verification loop, and rollback/abort policy are created by later authorized packages.

## Validation requirements

A validator must confirm that the framework document exists, the decision-framework artifact exists, the notes exist, all no-authority flags remain false, committed SXR8.DE and CSPX.L close/date evidence remains unchanged, SMH remains skipped, funding posture remains not_funded_framework_only, and the next package is a client-language quality gate or a correction package.
