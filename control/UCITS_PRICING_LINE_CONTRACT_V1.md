# UCITS Pricing Line Contract V1

## Purpose

This contract defines the first non-authoritative UCITS pricing-line preflight for `market-predictions/weekly-etf-eu`.

The goal is to test whether verified UCITS exchange trading lines can be extracted and priced without mutating portfolio state, without treating U.S. ETF proxies as EU holdings, and without enabling production delivery.

## Decision framework boundary

Pricing-line preflight answers:

```text
Can a verified UCITS candidate trading line be resolved and tested by a market-data source?
```

It does **not** answer:

```text
Should this ETF be funded?
```

Pricing success alone must never promote a candidate to `fundable`.

## Input/state contract

The pricing preflight source of truth is:

```text
config/ucits_symbol_registry.yml
```

Only registry entries with:

```text
investability_status: verified_candidate_not_funded
```

may enter the first pricing-line preflight.

A pricing candidate must include:

```text
registry_id
isin
fund_name
provider
exchange
exchange_ticker
trading_currency
provider_symbol
pricing_symbol_yahoo
us_research_proxy
pricing_status
```

The following are excluded:

- funded portfolio positions;
- U.S.-listed ETF research proxies;
- candidates still marked `candidate_requires_verification`;
- policy-blocked ETCs or non-UCITS instruments;
- trading lines with missing exchange, ticker, trading currency or provider symbol.

## Output contract

The candidate extractor writes:

```text
output/pricing/ucits_pricing_candidates_YYYYMMDD_HHMMSS.json
```

The live/non-authoritative preflight writes:

```text
output/pricing/ucits_pricing_preflight_YYYYMMDD_HHMMSS.json
```

Both artifacts must clearly state:

```text
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

## Pricing authority

The first implementation may use `yfinance` / Yahoo-style symbols such as:

```text
CSPX.L
SXR8.DE
```

This is a pricing-line connectivity test only. It is not yet the final valuation-grade pricing authority.

## Operational runbook

1. Validate UCITS symbol registry.
2. Validate UCITS investability contract.
3. Extract pricing candidates from verified, non-funded UCITS registry entries.
4. Validate pricing candidate artifact.
5. Run non-authoritative pricing preflight.
6. Validate preflight artifact.
7. Do not mutate portfolio state.
8. Do not generate production PDFs.
9. Do not send email.

## Promotion rule

A candidate can move toward `fundable` only after a separate decision-framework review validates:

- instrument identity;
- UCITS/KID status;
- trading line;
- pricing reliability;
- liquidity/spread suitability;
- role in portfolio;
- risk and concentration impact.

Pricing connectivity alone is insufficient.
