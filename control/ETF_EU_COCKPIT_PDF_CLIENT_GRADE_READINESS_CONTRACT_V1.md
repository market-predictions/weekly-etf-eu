# ETF EU Cockpit PDF Client-Grade Readiness Contract V1

## Purpose

This contract defines the client-grade readiness contract and evidence gate required before any later delivery-preflight discussion can be reopened for the ETF EU cockpit PDF.

It does **not** make any PDF client-grade. It does **not** authorize production delivery, valuation-grade pricing, portfolio mutation, candidate promotion, funding authority, live data refresh, recipient activation, secrets configuration, SMTP configuration, delivery receipt creation or production manifest creation.

## Authority rule

```text
readiness_gate_status=contract_defined_not_passed
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
delivery_preflight_allowed=false
outbound_path_enabled=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
```

## Source context

WP15U accepted the WP15T premium Dutch refinement PDF as a review-only cockpit foundation:

```text
accept_as_review_only_premium_dutch_cockpit_foundation_not_delivery_grade
```

That acceptance is not a client-grade approval. WP15V converts the WP15U state into a formal readiness gate.

## Layer 1 - decision framework readiness

Before any later client-grade discussion, all decision framework gates below must pass:

```text
weekly_portfolio_posture_clear=true
funded_holding_action_labels_present=true
candidate_promotion_status_present=true
no_candidate_presented_as_funded_without_funding_authority=true
thesis_and_invalidation_present_for_funded_holdings_or_proposed_candidates=true
risk_posture_and_concentration_visible=true
no_us_listed_etf_presented_as_dutch_eu_holding=true
unsupported_products_blocked_or_policy_review=true
```

Minimum evidence:

1. The weekly portfolio posture is immediately clear on the first decision page.
2. Every funded holding has one action label: buy, hold, reduce, sell, review, watch or cash.
3. Every candidate has explicit promotion status.
4. No candidate is presented as funded unless funding authority exists.
5. Thesis and invalidation are present for every funded holding or proposed candidate.
6. Risk posture and concentration are visible.
7. No U.S.-listed ETF is presented as a Dutch/EU holding.
8. Unsupported products are visibly blocked or marked policy-review.

## Layer 2 - input/state contract readiness

Before any later client-grade discussion, all input/state contract gates below must pass:

```text
isin_first_identity_present=true
ucits_status_present=true
priips_kid_status_present=true
trading_line_present=true
exchange_ticker_present=true
trading_currency_present=true
pricing_symbol_present=true
latest_close_date_present=true
latest_close_present=true
pricing_source_present=true
pricing_freshness_status_present=true
ter_or_cost_status_present=true
replication_method_present_or_explicitly_unknown=true
distribution_policy_present_or_explicitly_unknown=true
hedged_unhedged_status_present_or_explicitly_unknown=true
liquidity_spread_evidence_present_or_review_needed=true
missing_evidence_not_silently_ignored=true
unresolved_data_blocks_valuation_grade_and_delivery_preflight=true
```

Minimum evidence:

1. Every investable or funded row is ISIN-first.
2. UCITS status is present.
3. PRIIPs/KID status is present.
4. Trading line, exchange ticker and trading currency are present.
5. Pricing symbol, latest close date, latest close, pricing source and pricing freshness status are present.
6. TER/cost status is present.
7. Replication method is present or explicitly unknown.
8. Distribution policy is present or explicitly unknown.
9. Hedged/unhedged status is present or explicitly unknown.
10. Liquidity/spread evidence is present or explicitly review-needed.
11. Missing evidence cannot be silently ignored.
12. Unresolved data must block valuation-grade and delivery-preflight status.

## Layer 3 - output contract readiness

Before any later client-grade discussion, all output contract gates below must pass:

```text
dutch_first_client_language=true
readable_cockpit_hierarchy=true
no_clipping_overlap_black_boxes_unreadable_text_or_broken_flow=true
tables_cards_used_for_holdings_investability_pricing_and_decisions=true
evidence_badges_useful_and_visible=true
delivery_or_no_delivery_authority_marker_visible_not_dominant=true
proxy_disclosure_visible=true
limitations_block_visible=true
governance_footer_visible=true
pdf_rendered_and_visually_reviewed_before_client_grade_claim=true
bilingual_parity_required_if_english_companion_exists=true
```

Minimum evidence:

1. Dutch-first client language is used.
2. The cockpit hierarchy is readable.
3. Render review shows no clipping, overlap, black boxes, unreadable small text or broken page flow.
4. Tables/cards are used for holdings, investability, pricing and decisions.
5. Evidence badges are useful and visible.
6. Delivery/no-delivery authority marker is visible but not visually dominant.
7. Proxy disclosure is visible.
8. Limitations block is visible.
9. Governance footer is visible.
10. The PDF is rendered and visually reviewed before any later client-grade claim.
11. Bilingual parity is required only if English companion output is created.

## Layer 4 - operational runbook readiness

Before any later client-grade discussion, all operational runbook gates below must pass:

```text
deterministic_build_command_exists=true
validator_command_exists=true
targeted_pytest_exists=true
rendered_pdf_review_evidence_exists=true
no_delivery_workflow_changed=true
no_recipients_secrets_smtp_changed=true
no_live_data_fetch_without_explicit_later_authority=true
no_portfolio_state_mutation_without_explicit_later_authority=true
no_production_manifest_or_delivery_receipt_without_explicit_later_authority=true
```

Minimum evidence:

1. A deterministic build command exists.
2. A validator command exists.
3. Targeted pytest exists.
4. Rendered PDF review evidence exists.
5. No delivery workflow changed.
6. No recipients, secrets or SMTP configuration changed.
7. No live data fetch occurs unless explicitly authorized by a later package.
8. No portfolio state mutation occurs unless explicitly authorized by a later package.
9. No production manifest or delivery receipt exists unless explicitly authorized by a later package.

## Blocking gates before client-grade

The cockpit PDF cannot be called client-grade until every item below passes:

```text
all_decision_framework_gates_pass=true
all_input_state_contract_gates_pass=true
all_output_contract_gates_pass=true
all_operational_runbook_gates_pass=true
unresolved_data_blocks_cleared_or_explicitly_accepted_by_policy=true
valuation_grade=false until pricing and reconciliation evidence pass
client_grade_claim=false until readiness audit passes
```

## Blocking gates before delivery preflight

Delivery preflight cannot be reopened until every item below passes:

```text
client_grade_claim=true from a later authorized readiness audit
delivery_preflight_authority_explicitly_granted=true
production_delivery=false until receipt and manifest authority exists
receipt_artifact_created=false until explicitly authorized
production_manifest_created=false until explicitly authorized
recipient_secrets_smtp_configuration_authorized=true before outbound path
```

## Consequence for next package

The next package should audit the current WP15T/WP15U PDF candidate against this readiness contract.

Recommended next package:

```text
ETF-EU-WP15W - ETF EU cockpit PDF readiness gate implementation audit, no delivery
```
