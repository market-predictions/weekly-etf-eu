# ETF-EU-WP15AG product facts evidence decision — 2026-07-03

## Decision

ETF-EU-WP15AG is completed as a product-facts evidence acquisition package for the currently priced UCITS fund.

## Authority

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15AG
source_work_package=ETF-EU-WP15AF
readiness_gate_status=product_facts_acquired_not_client_grade
review_only=true
client_grade_claim=false
delivery_preflight_allowed=false
production_delivery=false
funding_authority=false
valuation_grade=false
portfolio_mutation=false
```

## Evidence acquired

The product facts evidence artifact records ISIN-first evidence for:

```text
isin=IE00B5BMR087
fund_name=iShares Core S&P 500 UCITS ETF USD (Acc)
issuer=iShares / BlackRock
```

Resolved product-fact gaps:

```text
TER_or_ongoing_charge_evidence
replication_method_evidence
distribution_policy_evidence
hedged_unhedged_status_evidence
```

Trading-line mappings retained:

```text
SXR8.DE -> IE00B5BMR087
CSPX.L -> IE00B5BMR087
```

## Boundaries preserved

```text
WP15AG did not fetch new prices.
WP15AG did not change SXR8.DE or CSPX.L price evidence.
WP15AG did not regenerate or replace the PDF.
WP15AG did not change the renderer.
WP15AG did not change recommendation logic.
WP15AG did not mutate portfolio state.
WP15AG did not create funding authority.
WP15AG did not create valuation-grade authority.
WP15AG did not create client-grade report authority.
WP15AG did not enable delivery-preflight.
WP15AG did not touch delivery, SMTP, secrets, or recipient configuration.
WP15AG did not create a delivery receipt.
WP15AG did not create a production manifest.
```

## Remaining blockers

Client-grade blockers remain non-empty and include:

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

Delivery-preflight blockers remain non-empty and include:

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

## Next package

```text
ETF-EU-WP15AH — ETF EU pricing freshness and valuation reconciliation policy, no delivery
```
