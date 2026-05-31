# Weekly ETF EU Review OS — Phase 4 Valuation Pricing Changelog

**Date:** 2026-05-31  
**Repository:** `market-predictions/weekly-etf-eu`  
**Scope:** Non-mutating valuation-grade UCITS pricing authority preparation.

---

## Current issue

The EU repo had a working UCITS pricing-line preflight, but that preflight was explicitly non-authoritative. It could show that a symbol such as `CSPX.L` or `SXR8.DE` is reachable through yfinance-style connectivity, but it could not safely become portfolio valuation authority.

## Root cause

UCITS ETF identity is ISIN-first, while pricing authority is trading-line specific. A safe valuation row must be evaluated at:

```text
registry_id + ISIN + exchange + exchange_ticker + trading_currency + provider_symbol + source + observed_date + close + source_lineage
```

A reachable quote symbol is therefore not enough.

---

## Files added

```text
control/UCITS_VALUATION_PRICING_CONTRACT_V1.md
config/ucits_pricing_source_policy.yml
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
```

## Files changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
control/DECISION_LOG_EU.md
```

---

## Change summary

### 1. Valuation pricing contract added

Added a formal Phase 4 contract that separates:

1. decision framework;
2. input/state contract;
3. output contract;
4. operational runbook.

The contract states that valuation pricing can support future portfolio decisions, but cannot itself create funding authority, portfolio mutation, PDF generation or delivery.

### 2. Pricing source policy added

Added `config/ucits_pricing_source_policy.yml` with a conservative authority hierarchy:

```text
exchange_official -> preferred valuation source
twelve_data -> candidate valuation source after line verification
issuer_factsheet -> reference / stale-check only
yahoo_yfinance -> non-authoritative connectivity only
```

Current CSPX/SXR8 trading-line policies are seeded as `valuation_grade_pending`.

### 3. Valuation artifact builder added

Added `pricing/build_ucits_valuation_prices.py`.

It reads:

```text
config/ucits_symbol_registry.yml
config/ucits_pricing_source_policy.yml
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
```

It writes:

```text
output/pricing/ucits_valuation_prices_YYYYMMDD_HHMMSS.json
```

Current rows are intentionally written as:

```text
valuation_status: valuation_grade_pending
valuation_grade: false
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

Non-authoritative preflight evidence is preserved separately and explicitly blocked from valuation authority.

### 4. Valuation artifact validator added

Added `tools/validate_ucits_valuation_prices.py`.

It enforces that any future `valuation_grade: true` row must include:

```text
pricing_source
source_authority
observed_date
close
currency
source_lineage
completed_session: true
currency == trading_currency
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

It also blocks yfinance from becoming valuation-grade under the current policy.

### 5. Workflow wired

Updated `.github/workflows/send-weekly-etf-eu-report.yml` so the EU validation flow now performs:

```text
pricing candidate build/validation
non-authoritative preflight
valuation artifact build/validation
cash-only state validation
candidate report render/validation
no-delivery confirmation
artifact commit
```

The workflow still performs no portfolio mutation, no PDF generation and no email delivery.

---

## Expected validation markers

```text
UCITS_VALUATION_PRICING_POLICY_OK
UCITS_VALUATION_PRICES_OK
UCITS_VALUATION_PRICES_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```

## Current authority state after this change

```text
portfolio_mutation: false
production_delivery: false
funding_authority: false
valuation_grade_rows: 0
valuation_pending_rows: expected from verified candidates
```

## Next action

Run the EU bootstrap validation workflow through a new queue file and confirm that the valuation artifact is generated and committed under `output/pricing/`.
