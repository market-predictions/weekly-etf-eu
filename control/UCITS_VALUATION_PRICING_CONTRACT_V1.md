# UCITS Valuation Pricing Contract V1

## Purpose

This contract defines the valuation-grade UCITS pricing authority layer for `market-predictions/weekly-etf-eu`.

It sits after the non-authoritative UCITS pricing-line preflight and before any future portfolio funding, valuation-history mutation, report delivery, PDF generation or email send.

The contract exists to prevent this failure mode:

```text
a reachable quote symbol is accidentally treated as authoritative portfolio valuation
```

## Four-layer boundary

### 1. Decision framework

Valuation pricing answers:

```text
Can this verified UCITS trading line be valued from an approved pricing source with enough source/date/currency lineage for report-state authority?
```

It does **not** answer:

```text
Should this ETF be bought, funded, sold, increased or reduced?
```

A valuation-grade price can support future funding decisions, but it cannot create funding authority by itself.

### 2. Input/state contract

The authoritative inputs are:

```text
config/ucits_symbol_registry.yml
config/ucits_pricing_source_policy.yml
control/DATA_SOURCE_METADATA.md
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
```

The registry remains ISIN-first. Pricing authority is evaluated at trading-line level:

```text
registry_id
isin
exchange
exchange_ticker
trading_currency
provider_symbol
pricing_source
observed_date
close
currency
source_lineage
completed_session
```

The non-authoritative preflight may be used as evidence of connectivity or display continuity only. It cannot create a valuation-grade row unless the source policy, source metadata, and agreement gate explicitly allow that source for that exact trading line.

### 3. Output contract

The valuation builder writes:

```text
output/pricing/ucits_valuation_prices_YYYYMMDD_HHMMSS.json
```

Every artifact and every row must state:

```text
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

Rows may be present with:

```text
valuation_status: valuation_grade_pending
valuation_grade: false
```

That is expected until approved valuation sources are integrated and verified.

A row may claim:

```text
valuation_status: valuation_grade
valuation_grade: true
```

only if the validator can confirm all required source, date, close, currency, completed-session and source-lineage evidence, and only if the agreement gate confirms sufficient independent market-close agreement evidence under source metadata policy.

### 4. Operational runbook

1. Validate the UCITS registry.
2. Validate the investability contract.
3. Build UCITS pricing candidates.
4. Validate pricing candidates.
5. Run non-authoritative pricing preflight.
6. Build the valuation pricing artifact.
7. Validate the valuation pricing artifact.
8. Keep portfolio state cash-only.
9. Do not produce a production PDF.
10. Do not send email.

## Source authority hierarchy

Source authority is configured in:

```text
config/ucits_pricing_source_policy.yml
```

Default hierarchy:

1. `exchange_official` / venue-specific official exchange candidates — preferred valuation source when a completed-session official close is available and attributable.
2. `twelve_data` — diagnostic/candidate source only after symbol/date/currency evidence and plan/source terms are verified for the specific UCITS trading line.
3. `issuer_factsheet` / issuer NAV references — reference-only or stale-check sources, not daily close authority unless explicitly upgraded by a separate contract.
4. `yahoo_yfinance` — non-authoritative connectivity/display source by default.

`yahoo_yfinance` must remain non-authoritative unless a future decision log entry and validator-backed implementation explicitly promote it for a specific trading line and document the reason. Under the current policy it cannot be agreement-gate valuation-grade authority.

## Agreement-gate source-counting rule

A source may count as independent market-close agreement evidence only when source metadata and source policy both allow it.

Current non-counting sources:

```text
yahoo_yfinance
issuer_nav
blackrock_issuer_reference
issuer_factsheet
stooq
boerse_frankfurt
twelve_data
```

Current candidate counting sources are limited to reviewed or review-pending venue/official close candidates such as:

```text
euronext_live
deutsche_boerse_live
exchange_official
```

A Yahoo/yfinance observed close may be preserved as provisional connectivity/display evidence, but it must not satisfy `min_independent_sources`, must not populate valuation authority fields, and must not flip `valuation_grade` to `true` under the current agreement-gate policy.

## Completed-session rule

A valuation-grade price must represent a completed regular market session for the exchange trading line being valued.

A valuation-grade row must include:

```text
observed_date
completed_session: true
session_rule
```

The artifact must not fabricate same-day closes. If the latest completed session is unavailable or unclear, the row must remain pending or blocked.

## Currency rule

A valuation-grade price must use the same currency as the trading line unless an explicit FX conversion layer is introduced later.

For Phase 4 bootstrap:

```text
currency == trading_currency
```

is required for any `valuation_grade: true` row.

## Stale-price rule

A stale price cannot be valuation-grade.

The source policy defines max calendar-day age. If that threshold is exceeded, the row must be blocked or pending.

## Required valuation-grade row fields

A row with `valuation_grade: true` must include all of:

```text
registry_id
isin
exchange
exchange_ticker
trading_currency
provider_symbol
pricing_source
source_authority
observed_date
close
currency
source_lineage
agreement_gate_evidence
valuation_grade: true
completed_session: true
portfolio_mutation: false
production_delivery: false
funding_authority: false
```

## Non-mutation rule

This valuation layer is evidence production only.

It must not update:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
```

until a later funding/promotion contract exists.

## Promotion boundary

A UCITS candidate may move toward `fundable` only after a separate promotion decision validates:

- UCITS identity and ISIN;
- PRIIPs/KID availability;
- broker/trading-line availability for the intended Dutch/EU client;
- valuation-grade pricing source;
- liquidity and spread suitability;
- portfolio role;
- concentration/risk impact;
- explicit decision-framework approval.

Pricing authority alone is never portfolio authority.
