# ETF EU client-grade authority decision policy v1

## Purpose

Define the explicit client-grade authority decision for the ETF EU review surface after the review-only evidence chain and Dutch-first language gate have passed.

## Scope

This policy creates only a client-grade authority decision. It applies to the committed evidence chain through ETF-EU-WP15AK.

## Authority boundary

This policy creates only a client-grade authority decision.

This policy does not enable delivery-preflight.

This policy does not create production delivery.

This policy does not create valuation-grade authority.

This policy does not create funding authority.

This policy does not mutate portfolio state.

This policy does not fetch new prices.

This policy does not regenerate or replace the PDF.

## Evidence-chain sufficiency requirements

A positive authority decision requires product facts evidence, pricing freshness policy, valuation reconciliation policy, PRIIPs/KID availability evidence, liquidity/spread evidence, investment thesis framework, invalidation criteria framework, funding posture framework, and client language quality gate to be present and validated from committed artifacts.

## Source-authority sufficiency requirements

A positive authority decision requires a traceable source manifest, issuer reference, registry reference, pricing artifact reference, and explicit disclosure of authority limitations.

## Pricing evidence limitation

Pricing evidence may support client-grade report state only. Pricing evidence does not become delivery-preflight evidence, valuation-grade evidence, execution evidence, or portfolio valuation evidence in this package.

## Valuation-grade limitation

A positive client-grade authority decision does not authorize valuation.

## Funding limitation

A positive client-grade authority decision does not authorize funding.

## Portfolio mutation limitation

A positive client-grade authority decision does not authorize portfolio mutation.

## Delivery-preflight limitation

A positive client-grade authority decision authorizes a client-grade report state only.

A positive client-grade authority decision does not authorize sending the report.

Delivery-preflight remains blocked until a later package creates and validates the delivery contract, operational runbook, verification loop, and rollback/abort policy.

## Positive authority decision rule

If every evidence-chain, source-authority, client-language, and pricing evidence sufficiency check passes, create client-grade authority for report state only with delivery blocked.

## Negative authority decision rule

If any evidence-chain, source-authority, client-language, or pricing evidence sufficiency check fails, keep client-grade authority false and route to a correction package.

## Validation requirements

A validator must confirm the policy exists, the authority decision artifact exists, the notes exist, the selected branch is internally consistent, fixed prices are unchanged, delivery remains blocked, no live price fetch occurred, no pricing evidence changed, no PDF was regenerated, no renderer changed, valuation-grade remains false, funding authority remains false, portfolio mutation remains false, and selected_next_package is either ETF-EU-WP15AM or ETF-EU-WP15AL-FIX.
