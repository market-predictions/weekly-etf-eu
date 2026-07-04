# ETF EU pricing freshness policy v1

## Purpose

Define deterministic review-only rules for interpreting close-date freshness in the ETF EU cockpit without fetching prices, changing price evidence, or creating client-grade, valuation-grade, funding, portfolio, or delivery authority.

## Scope

This policy applies to the existing WP15AB/WP15AC review-only cockpit pricing rows and later validators that classify close-date freshness. It is a policy layer only.

## Authority boundary

```text
review_only=true
pricing_freshness_policy_created=true
client_grade_claim=false
delivery_preflight_allowed=false
production_delivery=false
funding_authority=false
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
live_price_fetch_performed=false
pricing_evidence_changed=false
new_pdf_created=false
renderer_changed=false
```

## Freshness categories

```text
current_completed_session = close date matches the latest completed regular exchange session already present in the fixed artifact
one_trading_day_lag = close date is one completed trading day behind the expected completed session but may remain useful for review-only context
stale_but_reviewable = close date is older than one trading day but can still be shown with explicit stale status in review-only context
stale_blocking = close date is too old, inconsistent, or insufficiently explained for any client-grade or delivery-preflight use
unpriced_or_pending_verification = line has no valid close because the symbol, exchange line, or provider status remains pending, skipped, or failed
```

Required category identifiers:

```text
current_completed_session
one_trading_day_lag
stale_but_reviewable
stale_blocking
unpriced_or_pending_verification
```

## Completed-session rule

A close date may only be classified against completed sessions already present in committed artifacts. WP15AH must not query markets or infer a newer close. A close date alone is not valuation-grade evidence.

## Weekend and exchange-holiday handling

Weekend or exchange-holiday gaps do not automatically make a close stale. A validator may classify an existing close as current for review-only purposes when the committed artifact already records that close as the latest completed session. This policy does not create a holiday calendar and does not authorize external date checks.

## Multi-line close-date handling

Line-level freshness must remain separate. If one line is current and another same-ISIN line is older, the line-level freshness status must remain separate. A same-ISIN mapping cannot be used to overwrite, fill, or normalize another line's close date.

## Stale-price handling

Stale prices must be labelled by policy status. Skipped or pending-verification rows remain unpriced and cannot be inferred from another ticker. SMH remains skipped_pending_registry_status. No price may be fetched or edited by this policy package.

## Review-only interpretation

A successful provider close may support review-only analysis but does not authorize client-grade reporting. Review-only output may show committed line-level close evidence with explicit freshness labels.

## Client-grade limitation

This policy is necessary but not sufficient for client-grade status. Client-grade status remains blocked until all required evidence gates pass, including investability, liquidity/spread, decision framework, and client-language quality gates.

## Delivery-preflight limitation

Delivery-preflight authority remains false. This policy does not authorize outbound delivery, delivery receipts, production manifests, SMTP/secrets changes, or recipient configuration changes.

## Non-authorized actions

WP15AH does not authorize:

```text
new price fetches
manual price edits
intraday prices
FX conversion
portfolio valuation
funding decisions
PDF regeneration
renderer changes
recommendation logic changes
recipient configuration changes
SMTP or secret configuration changes
delivery receipts
production manifests
```

## Required future evidence before client-grade

At minimum, the following remain required before client-grade authority can be considered:

```text
investment_thesis_for_proposed_funded_positions
invalidation_criteria_for_proposed_funded_positions
funding_decision_or_cash_posture
PRIIPs_KID_availability_evidence
liquidity_spread_evidence
client_language_quality_gate
all delivery-preflight blockers after client-grade gates pass
```

## Validation requirements

A validator must confirm that this policy exists, contains all required sections, defines all freshness categories, keeps all no-authority flags false, preserves existing SXR8.DE and CSPX.L close/date evidence, keeps SMH unpriced/pending, and does not create valuation-grade, client-grade, or delivery-preflight authority.
