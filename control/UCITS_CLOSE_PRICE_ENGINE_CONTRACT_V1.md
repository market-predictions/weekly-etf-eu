# UCITS Close Price Engine Contract V1

## Purpose

This contract defines the generic close-price engine for `market-predictions/weekly-etf-eu`.

It replaces the idea of hard-coding individual Euronext or Deutsche Boerse pages as the long-term pricing solution.

The engine is ISIN/trading-line/source-adapter based.

## Current issue

European UCITS ETFs cannot be priced reliably from ticker text alone.

A single UCITS fund can have:

- one ISIN;
- multiple exchange trading lines;
- multiple tickers;
- multiple trading currencies;
- multiple market identifiers;
- multiple data-provider symbol conventions.

Therefore a generic EU price engine must not mean:

```text
Any ticker string always produces a reliable close.
```

It must mean:

```text
Given an ISIN-first UCITS instrument, a verified trading line, and a source-policy registry, the engine can route the request to reusable source adapters and emit standardized close observations with blockers.
```

## Four-layer boundary

### 1. Decision framework

The close-price engine does not decide whether an ETF deserves capital.

It only answers:

```text
Can this trading line produce a sufficiently evidenced close observation from a configured source adapter?
```

### 2. Input/state contract

Inputs:

```text
config/ucits_symbol_registry.yml
config/ucits_pricing_source_policy.yml
output/pricing/ucits_pricing_candidates_*.json
```

The engine key is:

```text
registry_id + isin + exchange + exchange_ticker + trading_currency + source_id + adapter_name
```

Ticker alone is never enough.

### 3. Output contract

The engine writes:

```text
output/pricing/ucits_close_observations_YYYYMMDD_HHMMSS.json
```

Every top-level artifact and every row must preserve:

```text
portfolio_mutation: false
production_delivery: false
funding_authority: false
valuation_authority: false
```

### 4. Operational runbook

The engine should run after:

1. UCITS registry validation;
2. UCITS pricing-candidate extraction;
3. source-policy validation.

The engine may run before valuation-grade promotion, but it must not itself mutate portfolio state or valuation history.

## Standard observation row

Each row must include:

```text
registry_id
isin
exchange
exchange_ticker
trading_currency
provider_symbol
source_id
adapter_name
source_url
observation_status
candidate_close
candidate_date
candidate_currency
completed_session
confidence
parser_status
blockers
source_lineage
portfolio_mutation=false
production_delivery=false
funding_authority=false
valuation_authority=false
```

## Adapter interface

Each adapter should implement:

```text
supports(source_policy, trading_line) -> bool
observe(source_policy, trading_line) -> CloseObservation
```

Adapters must not write state files directly.

Adapters must return blockers instead of raising fatal errors for normal source failures.

## Initial adapters

Initial adapters:

- `euronext_live` — official Euronext source adapter candidate.
- `deutsche_boerse_live` — official Deutsche Boerse / Xetra adapter candidate.
- `twelve_data_diagnostic` — diagnostic only under the current non-upgrade decision.
- `yahoo_connectivity` — non-authoritative connectivity only.

## Promotion boundary

A close observation with a candidate close is not automatically valuation-grade.

A separate promotion/validator must verify:

- source authority;
- observed date;
- completed session;
- currency equals trading currency unless an explicit FX layer exists;
- positive close;
- source lineage;
- acceptable staleness;
- no portfolio mutation;
- no delivery authority.

Only then may a later artifact set:

```text
valuation_grade: true
```

## Current Phase 4 authority

During Phase 4, the close-price engine remains evidence-only.

Expected current behavior:

```text
candidate_close: null or observed evidence only
valuation_authority: false
funding_authority: false
portfolio_mutation: false
production_delivery: false
```

## Design decision

The current official page-evidence artifacts are source research.

They should inform adapter design, but should not become the long-term generic price engine.
