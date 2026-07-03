# ETF EU Cockpit PDF Readiness Evidence Acquisition Contract V1

## Purpose

This contract defines the minimum evidence acquisition contract needed before the ETF EU cockpit PDF can progress from review-only pricing proof-of-concept toward a broader evidence-complete preview.

WP15Y is intentionally practical: it creates a first closing-price proof-of-concept for one EU UCITS trading line while preserving all no-delivery, no-portfolio, no-funding and non-valuation-grade boundaries.

## Evidence classes

```text
registry evidence
pricing evidence
fund facts evidence
liquidity/spread evidence
decision evidence
rendered output evidence
```

## Required evidence fields

The full future evidence contract must cover:

```text
isin
fund_name
ucits_status
priips_kid_status
exchange
exchange_ticker
trading_currency
pricing_symbol
latest_close_date
latest_close
pricing_source
pricing_fetch_timestamp
pricing_freshness_status
ter_pct
replication_method
distribution_policy
hedged_unhedged_status
liquidity_spread_status
candidate_thesis
candidate_invalidation
decision_status
```

## First proof-of-concept scope

The first POC target is:

```text
isin=IE00B5BMR087
fund_name=iShares Core S&P 500 UCITS ETF USD (Acc)
exchange=Xetra
exchange_ticker=SXR8
trading_currency=EUR
pricing_symbol=SXR8.DE
```

## POC authority

```text
limited_pricing_poc_performed=true
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
portfolio_mutation=false
funding_authority=false
candidate_promotion=false
production_delivery=false
```

A successful POC proves only that one registry trading line can be connected to a provider close. It does not prove client-grade valuation, delivery readiness, portfolio authority, recommendation validity or complete evidence coverage.

## Provider behavior

The POC runner must not fake a price. If provider access fails, the artifact must still be written with a clear failure status and a null close.

Allowed result states:

```text
provider_status=success
provider_status=failed
```

Required failure behavior:

```text
pricing_poc_status=failed_provider_or_symbol_unavailable
latest_close=null
provider_error=<clear reason>
```

## Next contract step

If the POC succeeds, the next package may render the close into a cockpit PDF preview surface.

If the POC fails, the next package must repair provider access or symbol mapping before attempting a PDF pricing preview.
