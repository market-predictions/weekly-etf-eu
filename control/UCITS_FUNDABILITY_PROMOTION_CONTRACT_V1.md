# UCITS Fundability Promotion Contract V1

## Purpose

This contract defines when a UCITS candidate may move from research/pricing candidate status toward `fundable` status in the Weekly ETF EU Review system.

It does not fund any instrument, mutate portfolio state, create a recommendation, or enable delivery.

## Authority boundary

A candidate may not become funded or fundable from pricing evidence alone.

The following must remain false unless a later explicit implementation and decision log entry changes them:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
```

## Status distinction

```text
verified_candidate_not_funded
```

means the instrument has enough registry quality for research and pricing tests. It does **not** mean that capital may be allocated.

```text
fundable
```

requires all gates below to pass.

## Required promotion gates

A candidate can be marked `fundable` only after all of these gates pass:

1. **Instrument identity gate**
   - ISIN is present and not placeholder.
   - Fund name and provider are present.
   - Instrument type is UCITS ETF or explicitly accepted by policy.
   - U.S. proxy is marked research-only.

2. **EU investability gate**
   - UCITS status is confirmed.
   - PRIIPs/KID availability is confirmed for Dutch/EU clients.
   - Domicile, distribution policy, replication method, benchmark and TER are known.

3. **Trading-line gate**
   - At least one exchange line has verified exchange, ticker and trading currency.
   - Pricing symbol is verified for the specific trading line.
   - Trading currency is acceptable for the model.

4. **Pricing-quality gate**
   - Agreement-gate valuation status is available.
   - Pricing is not based solely on Yahoo/yfinance or issuer NAV/reference evidence.
   - Issuer NAV may support stale-check/reference only.
   - Valuation-grade promotion is allowed only after source policy and agreement gate permit it.

5. **Tradability/liquidity gate**
   - Liquidity and spread checks are present.
   - Broker availability is confirmed.
   - Any broker-specific venue/currency limitations are recorded.

6. **Portfolio role gate**
   - Candidate role is explicit.
   - It has been compared against current exposure and alternatives.
   - Concentration, overlap and risk contribution are reviewed.

7. **Decision gate**
   - A separate portfolio decision explicitly approves promotion.
   - Promotion is recorded in the decision log or equivalent control artifact.
   - No automatic promotion from report display or pricing success is allowed.

## Blocking conditions

A candidate must remain not fundable if any of these are true:

```text
is_us_listed_holding=true
instrument_type=ETC under UCITS-only policy
ucits_status missing or negative
priips_kid_status missing or negative
trading line missing or pending
pricing symbol pending
pricing evidence provisional only
valuation_grade=false
liquidity/spread unknown
broker availability unknown
portfolio decision missing
```

## Current bootstrap decision

All current registry candidates remain non-funded. CSPX may continue through research and pricing tests, but it is not fundable until the gates above are satisfied and a separate promotion decision is recorded.
