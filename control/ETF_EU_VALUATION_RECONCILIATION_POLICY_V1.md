# ETF EU valuation reconciliation policy v1

## Purpose

Define deterministic review-only rules for interpreting same-ISIN, multi-trading-line evidence without performing valuation reconciliation or creating valuation-grade, client-grade, funding, portfolio, or delivery authority.

## Scope

This policy applies to committed ETF EU artifacts where more than one trading line maps to the same UCITS fund. It defines reconciliation semantics only; it does not calculate value.

## Authority boundary

```text
review_only=true
valuation_reconciliation_policy_created=true
client_grade_claim=false
delivery_preflight_allowed=false
production_delivery=false
funding_authority=false
valuation_grade=false
portfolio_mutation=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
live_price_fetch_performed=false
pricing_evidence_changed=false
new_pdf_created=false
renderer_changed=false
```

## ISIN-first reconciliation principle

ISIN is the canonical fund identity. Trading symbols identify exchange lines only. A same-ISIN trading-line mapping is identity evidence, not valuation-grade equivalence.

## Trading-line reconciliation

SXR8.DE and CSPX.L map to the same ISIN IE00B5BMR087 but remain distinct trading lines. Their exchange, trading currency, close, source timestamp, and line status must remain line-level facts.

## Currency-aware interpretation

EUR and USD trading currencies must not be collapsed into one valuation without an explicit FX and broker execution policy. WP15AH must not perform FX conversion or infer cross-currency equivalence from price levels.

## Same-fund line mapping

Same-fund line mapping may support identity review and line comparison, but it does not authorize funded status, portfolio valuation, recommendation changes, or delivery.

## Close-date mismatch handling

If same-ISIN lines have different close dates, each line keeps its own freshness status. A current line cannot make another stale or skipped line current.

## Price-source mismatch handling

If same-ISIN lines use different sources or source timestamps, those sources remain line-level evidence. A successful source for one line cannot repair another line's failed, skipped, stale, or pending status.

## Review-only valuation posture

WP15AH may define reconciliation rules but may not perform valuation reconciliation. Review-only artifacts may state that same-ISIN lines map to one fund while preserving distinct line-level price evidence.

## Why this is not valuation-grade

No portfolio value may be calculated from these lines in WP15AH. No line may be promoted to funded status in WP15AH. No FX policy, broker execution policy, liquidity/spread policy, or portfolio state mutation is created here.

## Client-grade limitation

This policy is necessary but not sufficient for client-grade status. Client-grade authority remains false until all evidence gates pass in later authorized packages.

## Delivery-preflight limitation

Delivery-preflight remains blocked. This policy does not authorize outbound delivery, recipient configuration, SMTP/secrets configuration, delivery receipts, or production manifests.

## Non-authorized actions

WP15AH does not authorize:

```text
valuation-grade reconciliation
portfolio value calculation
currency conversion
funding decisions
position sizing
candidate promotion
new price fetches
manual price edits
PDF regeneration
renderer changes
delivery-preflight
production delivery
```

## Required future evidence before valuation-grade or client-grade

Before valuation-grade or client-grade authority can be considered, later packages must supply at least:

```text
explicit FX and broker execution policy if cross-currency valuation is required
liquidity_spread_evidence
PRIIPs_KID_availability_evidence
funding_decision_or_cash_posture
investment_thesis_for_proposed_funded_positions
invalidation_criteria_for_proposed_funded_positions
client_language_quality_gate
all delivery-preflight blockers after client-grade gates pass
```

## Validation requirements

A validator must confirm that this policy exists, contains all required sections, preserves the same-ISIN line mapping for SXR8.DE and CSPX.L, keeps trading currencies line-level, blocks FX conversion and portfolio valuation, keeps SMH skipped/pending, and leaves valuation-grade, client-grade, funding, portfolio, and delivery authority false.
