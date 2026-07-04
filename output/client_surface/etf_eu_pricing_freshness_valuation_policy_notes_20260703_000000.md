# ETF-EU-WP15AH pricing freshness and valuation reconciliation policy

## Scope

WP15AH defines policy only.

WP15AH does not fetch new prices.

WP15AH does not change existing price evidence.

WP15AH does not regenerate or replace the PDF.

WP15AH does not make the report client-grade.

WP15AH does not create valuation-grade authority.

Delivery-preflight authority remains false.

Production delivery remains false.

## Source artifacts

```text
source_work_package=ETF-EU-WP15AG
source_product_facts_artifact=output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json
source_product_facts_notes=output/client_surface/etf_eu_product_facts_evidence_notes_20260703_000000.md
source_acquisition_plan_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json
source_gap_audit_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json
source_readiness_gate_artifact=output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_20260703_000000.json
source_review_only_pdf=output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf
source_pricing_artifact=output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json
```

## Policy documents

```text
pricing_freshness_policy_path=control/ETF_EU_PRICING_FRESHNESS_POLICY_V1.md
valuation_reconciliation_policy_path=control/ETF_EU_VALUATION_RECONCILIATION_POLICY_V1.md
```

## Pricing freshness policy

Defined freshness categories:

```text
current_completed_session
one_trading_day_lag
stale_but_reviewable
stale_blocking
unpriced_or_pending_verification
```

A close date alone is not valuation-grade evidence. A successful provider close may support review-only analysis but does not authorize client-grade reporting.

## Valuation reconciliation policy

Defined reconciliation rules:

```text
isin_first_identity_required
same_isin_lines_may_map_to_same_fund
trading_currency_must_remain_line_level
no_fx_conversion_without_authorized_fx_policy
no_portfolio_valuation_without_valuation_grade_authority
skipped_lines_cannot_be_inferred_from_related_lines
review_only_prices_do_not_authorize_delivery
```

SXR8.DE and CSPX.L map to the same ISIN IE00B5BMR087 but remain distinct trading lines. EUR and USD trading currencies must not be collapsed into one valuation without an explicit FX and broker execution policy.

## Current line classifications

```text
SXR8.DE -> current_completed_session
CSPX.L -> current_completed_session
SMH -> unpriced_or_pending_verification
```

These are policy classifications of existing committed artifacts only. No dates or closes were refetched.

## Resolved policy gaps

```text
price_freshness_policy
valuation_reconciliation_policy
```

## Remaining client-grade blockers

```text
investment_thesis_for_proposed_funded_positions
invalidation_criteria_for_proposed_funded_positions
funding_decision_or_cash_posture
PRIIPs_KID_availability_evidence
liquidity_spread_evidence
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
pricing_freshness_policy_created=true
valuation_reconciliation_policy_created=true
pricing_freshness_policy_validated=true
valuation_reconciliation_policy_validated=true
readiness_gate_status=pricing_and_valuation_policy_defined_not_client_grade
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
ETF-EU-WP15AH completed pricing freshness and valuation reconciliation policy definition only.
The price_freshness_policy and valuation_reconciliation_policy gaps are resolved as internal policy artifacts.
The report is not client-grade.
Valuation-grade authority remains false.
Delivery-preflight remains blocked.
Production delivery remains false.
No pricing evidence was changed.
No PDF was regenerated or replaced.
No renderer was changed.
```

## Next package

```text
ETF-EU-WP15AI — ETF EU PRIIPs/KID and liquidity/spread investability evidence, no delivery
```
