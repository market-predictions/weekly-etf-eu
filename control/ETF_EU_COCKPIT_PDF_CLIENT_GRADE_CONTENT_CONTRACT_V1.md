# ETF EU Cockpit PDF Client-Grade Content Contract V1

## Purpose

This contract defines the minimum content-completeness threshold for the ETF EU cockpit PDF before any later delivery-preflight discussion may be reopened.

It does **not** authorize delivery, valuation-grade pricing, portfolio mutation, candidate promotion, funding authority, live data refresh, recipient activation, secrets configuration, SMTP configuration, production manifests or delivery receipts.

## Decision framework layer

The cockpit PDF must answer the client decision question clearly:

```text
Which UCITS ETFs available to Dutch/EU investors deserve capital this week, and which positions require review, reduction, replacement or no action?
```

Minimum decision content:

1. portfolio posture / weekly decision summary;
2. holding-level action labels: buy, hold, reduce, sell, review, watch or cash;
3. thesis and invalidation trigger per active holding or candidate;
4. risk posture and portfolio concentration read;
5. named alternatives for weak or replaceable exposures;
6. clear separation between investable UCITS ETFs and U.S. research proxies;
7. explicit statement where no funding authority or candidate promotion exists.

## Input/state contract layer

Every investable or funded ETF row shown as a portfolio holding must be ISIN-first and UCITS-first.

Required visible fields for funded holdings or proposed investable UCITS candidates:

```text
isin
fund_name
provider
ucits_status
priips_kid_status
exchange_ticker
trading_currency
primary_exchange
pricing_symbol
latest_close_date
latest_close
pricing_source
pricing_freshness_status
ter_or_cost_status
replication_method_or_unknown
distribution_policy_or_unknown
hedged_unhedged_or_unknown
```

Required state/evidence rules:

- U.S.-listed ETFs may appear only as research proxies, benchmarks or signal inputs.
- Pricing evidence must disclose source and freshness per trading line.
- Unresolved pricing rows must be explicit and must not silently freeze a whole portfolio.
- Portfolio totals and visible valuation rows must reconcile if a valuation surface is shown.
- Any missing KID, UCITS, liquidity, TER or replication evidence must be marked as missing or review-needed.

## Output contract layer

A client-grade cockpit PDF must include these minimum visible sections:

1. cockpit header with report date, status, no-delivery/authority markers where applicable;
2. executive read / action summary;
3. portfolio holdings and cash snapshot;
4. allocation and concentration summary;
5. UCITS investability table;
6. pricing and freshness evidence table;
7. holding-level decision table;
8. watchlist / candidate pipeline with promotion status;
9. risk, regime and event context relevant to the ETF decisions;
10. proxy / benchmark disclosure that prevents U.S. ETFs from being read as EU holdings;
11. unresolved-data and limitation block;
12. validation / governance footer.

The Dutch report remains the primary client-facing output for the EU model. English output may exist as companion or audit surface only if bilingual parity rules are satisfied.

## Operational runbook layer

Before any delivery-preflight discussion, validators must confirm:

```text
content_completeness=true
no_us_etf_as_eu_holding=true
isin_first_holdings=true
ucits_status_present=true
priips_kid_status_present=true
pricing_source_and_freshness_present=true
portfolio_reconciliation_present_when_valuation_shown=true
proxy_disclosure_present=true
unresolved_data_block_present=true
bilingual_or_dutch_quality_gate_required=true
delivery_boundary_markers_present=true
production_delivery=false
receipt_artifact_created=false
production_manifest_created=false
```

## Authority boundary

This contract is a content completeness contract only.

```text
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

## Consequence for next package

After this contract, the next implementation package may build a review-only content-complete cockpit PDF candidate against this contract.

Recommended next package:

```text
ETF-EU-WP15R — ETF EU cockpit PDF content-complete candidate build, no delivery
```
