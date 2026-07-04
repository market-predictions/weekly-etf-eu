# ETF-EU-WP15AI PRIIPs/KID and liquidity/spread investability evidence

## Scope

WP15AI acquires investability evidence only.

WP15AI does not fetch new close prices.

WP15AI does not change existing price evidence.

WP15AI does not regenerate or replace the PDF.

WP15AI does not change the renderer.

WP15AI does not calculate valuation.

WP15AI does not create funding authority.

WP15AI does not make the report client-grade.

WP15AI does not create valuation-grade authority.

Delivery-preflight authority remains false.

Production delivery remains false.

## Source artifacts

```text
source_work_package=ETF-EU-WP15AH
source_policy_artifact=output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json
source_product_facts_artifact=output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json
source_pricing_artifact=output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json
source_registry=config/ucits_symbol_registry.yml
source_review_only_pdf=output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf
```

## Source manifest

WP15AI uses internal artifacts, the UCITS symbol registry, the official iShares product-page reference recorded in the registry, and review-only exchange-line references for SXR8.DE and CSPX.L.

Public web search did not return deterministic usable source pages during WP15AI packaging. Therefore, spread values are not used, and exchange-line spread evidence remains `needs_cross_check` before any client-grade or valuation-grade use.

## Fund-level PRIIPs/KID evidence

```text
isin=IE00B5BMR087
fund_name=iShares Core S&P 500 UCITS ETF USD (Acc)
issuer=iShares / BlackRock
priips_kid_status=available
priips_kid_document_available=true
priips_kid_authority_level=official_issuer
priips_kid_confidence=needs_cross_check
```

The PRIIPs/KID evidence is review-only. The exact language-specific KID document remains a later direct-document cross-check item before client-grade authority.

## Line-level liquidity/spread evidence

```text
SXR8.DE
exchange=Xetra
trading_currency=EUR
liquidity_evidence_status=available
spread_evidence_status=needs_cross_check
liquidity_confidence=needs_cross_check
spread_confidence=needs_cross_check
```

```text
CSPX.L
exchange=London Stock Exchange
trading_currency=USD
liquidity_evidence_status=available
spread_evidence_status=needs_cross_check
liquidity_confidence=confirmed
spread_confidence=needs_cross_check
```

No spread value is used. No execution price, trade size, slippage estimate, or portfolio value is calculated.

## Resolved investability gaps

```text
PRIIPs_KID_availability_evidence
liquidity_spread_evidence
```

These are resolved as review-only investability evidence states, not client-grade or valuation-grade evidence.

## Remaining client-grade blockers

```text
investment_thesis_for_proposed_funded_positions
invalidation_criteria_for_proposed_funded_positions
funding_decision_or_cash_posture
client_language_quality_gate
```

## Remaining delivery-preflight blockers

```text
all_client_grade_gates_passed
delivery_receipt_or_manifest_contract
recipient_configuration_authority
SMTP_secret_authority
production_delivery_manifest_path
outbound_runbook
post_send_verification_loop
rollback_or_abort_policy
```

## Boundary checks

```text
review_only=true
priips_kid_evidence_acquired=true
liquidity_spread_evidence_acquired=true
investability_evidence_validated=true
readiness_gate_status=investability_evidence_acquired_not_client_grade
accepted_review_only_foundation=true
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
delivery_preflight_allowed=false
delivery_authorization_decision=remain_blocked
outbound_path_enabled=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
receipt_artifact_created=false
production_manifest_created=false
recipient_config_changed=false
smtp_or_secret_config_changed=false
fake_price_used=false
us_proxy_price_used=false
live_price_fetch_performed=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
source_pdf_replaced=false
new_pdf_created=false
renderer_changed=false
```

## Decision

```text
ETF-EU-WP15AI completed review-only PRIIPs/KID and liquidity/spread investability evidence acquisition.
The PRIIPs/KID availability and liquidity/spread evidence gaps are resolved as review-only evidence states.
The report is not client-grade.
Valuation-grade authority remains false.
Funding authority remains false.
Portfolio mutation remains false.
Delivery-preflight remains blocked.
Production delivery remains false.
No close prices were fetched or changed.
No PDF was regenerated or replaced.
No renderer was changed.
```

## Next package

```text
ETF-EU-WP15AJ — ETF EU investment thesis, invalidation criteria, and funding posture framework, no delivery
```
