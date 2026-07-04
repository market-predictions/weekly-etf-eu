# ETF-EU-WP15AG product facts evidence

## Scope

Product facts were acquired for the current priced UCITS fund:

```text
isin=IE00B5BMR087
fund_name=iShares Core S&P 500 UCITS ETF USD (Acc)
issuer=iShares / BlackRock
```

The WP15AB/WP15AC PDF remains accepted only as review-only foundation.

WP15AG does not fetch new prices.

WP15AG does not make the report client-grade.

Delivery-preflight authority remains false.

Production delivery remains false.

## Source artifacts

```text
source_work_package=ETF-EU-WP15AF
source_acquisition_plan_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json
source_gap_audit_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json
source_review_only_pdf=output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf
source_pricing_artifact=output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json
source_registry=config/ucits_symbol_registry.yml
```

## Source manifest

```text
src_wp15af_acquisition_plan -> internal_artifact
src_wp15ae_gap_audit -> internal_artifact
src_wp15aa_multi_line_pricing -> internal_artifact
src_ucits_registry -> internal_artifact
src_ishares_product_page_253743 -> official_issuer
```

At least one official issuer source is recorded. Product-page evidence is attached as source reference and mapped into the product facts artifact.

## Fund-level evidence

```text
isin=IE00B5BMR087
fund_name=iShares Core S&P 500 UCITS ETF USD (Acc)
issuer=iShares / BlackRock
ucits_status=confirmed
product_structure=UCITS ETF
TER_or_ongoing_charge=0.07%
replication_method=physical_replication
distribution_policy=accumulating
hedged_unhedged_status=unhedged
fund_currency=USD
domicile=Ireland
source_authority_level=official_issuer
```

Confidence markers are stored in the JSON artifact under `fund_product_facts.field_confidence`.

The hedged/unhedged status is retained as product-fact evidence but marked `needs_cross_check` in the JSON artifact because WP15AG does not create a broader investability/KID evidence artifact.

## Trading-line evidence

```text
SXR8.DE
isin=IE00B5BMR087
exchange=Xetra
trading_currency=EUR
line_status=success
maps_to_same_fund=true
line_confidence=needs_cross_check
```

```text
CSPX.L
isin=IE00B5BMR087
exchange=London Stock Exchange
trading_currency=USD
line_status=success
maps_to_same_fund=true
line_confidence=confirmed
```

Both trading lines are treated as exchange trading lines of the same UCITS fund. This package does not acquire new prices and does not change prior close/date evidence.

## Resolved product-fact gaps

```text
TER_or_ongoing_charge_evidence
replication_method_evidence
distribution_policy_evidence
hedged_unhedged_status_evidence
```

## Remaining client-grade blockers

```text
investment_thesis_for_proposed_funded_positions
invalidation_criteria_for_proposed_funded_positions
funding_decision_or_cash_posture
PRIIPs_KID_availability_evidence
liquidity_spread_evidence
price_freshness_policy
valuation_reconciliation_policy
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
product_facts_evidence_acquired=true
product_facts_evidence_validated=true
readiness_gate_status=product_facts_acquired_not_client_grade
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
ETF-EU-WP15AG completed product-facts evidence acquisition for the current priced UCITS fund only.
The four product-fact gaps are resolved in a review-only evidence artifact.
The report is not client-grade.
Delivery-preflight remains blocked.
Production delivery remains false.
No pricing evidence was changed.
No PDF was regenerated or replaced.
No renderer was changed.
```

## Next package

```text
ETF-EU-WP15AH — ETF EU pricing freshness and valuation reconciliation policy, no delivery
```
