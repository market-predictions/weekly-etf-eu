# ETF EU client language quality gate v1

## Purpose

Define the Dutch-first client-language quality gate for ETF EU review surfaces and readiness synthesis.

## Scope

This policy validates wording only. It applies to review-only EU client surfaces that are built from committed evidence through ETF-EU-WP15AJ.

## Authority boundary

The client language gate validates wording only.

The client language gate does not create client-grade authority.

The client language gate does not create delivery-preflight authority.

The client language gate does not create valuation-grade authority.

The client language gate does not create funding authority.

The client language gate does not mutate portfolio state.

The client language gate does not send or authorize delivery.

## Dutch-first client-language standard

Client-facing wording must be Dutch-first, plain, conservative, and explicit about evidence status. English technical labels may remain in machine-readable artifacts, but client-facing synthesis must use Dutch wording first.

## Review-only disclosure requirements

Dutch-first client wording must disclose review-only status.

Required acceptable disclosure concepts:

```text
review-only
onder beoordeling
niet geschikt voor verzending
geen portefeuillewijziging
geen financieringsbesluit
```

## Source-authority wording requirements

Dutch-first client wording must disclose source-authority limitations. It must distinguish committed internal evidence, official issuer references, exchange-line evidence requiring cross-check, and skipped/pending symbols.

## Residual blocker disclosure requirements

Dutch-first client wording must disclose residual delivery-preflight blockers. It must not imply that a report can be sent, that delivery has been authorized, or that receipt/manifest evidence exists.

## Prohibited client-facing wording

Client-facing wording must avoid transaction, funding, allocation, and delivery-ready wording.

Prohibited wording includes:

```text
koopadvies
verkoopadvies
houden
nu financieren
nu alloceren
klaar voor verzending
client-grade zonder voorbehoud
waarderingswaardig
portefeuille-goedgekeurd
```

These terms may appear only inside prohibited-wording lists or explicit negations.

## Readiness synthesis rules

A readiness synthesis may say that review-only evidence/framework gates have been addressed and that the language quality gate passed.

A readiness synthesis must also say that client-grade authority remains false, delivery-preflight remains blocked, and production delivery remains false.

## Client-grade limitation

Zero remaining review-evidence blockers does not authorize client-grade output. Client-grade authority remains false until a later explicit authority package creates and validates the client-grade decision.

## Delivery-preflight limitation

Delivery-preflight remains blocked until a later explicit package creates and validates delivery authority, delivery contracts, operational runbook, verification loop, and rollback/abort policy.

## Validation requirements

A validator must confirm the policy exists, the synthesis artifact exists, language gate fields are present, readiness synthesis fields are present, fixed prices are unchanged, all no-authority flags remain false, remaining delivery-preflight blockers are non-empty, and selected_next_package is either ETF-EU-WP15AL or ETF-EU-WP15AK-FIX.
