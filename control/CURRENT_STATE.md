# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-05-30

## What this repository currently is

This repository has just been cloned from `market-predictions/weekly-etf` into:

```text
market-predictions/weekly-etf-eu
```

It is now the working environment for a European / Dutch-client UCITS ETF review system.

## Important baseline distinction

The original source repo remains:

```text
market-predictions/weekly-etf = U.S.-ETF model baseline
```

This new repo is intended to become:

```text
market-predictions/weekly-etf-eu = UCITS ETF model for Dutch/EU clients
```

The clone currently still contains many U.S.-ETF artifacts, workflow names and outputs. Those files are inherited history, not final EU authority.

## Current migration status

The repo is in **Phase 0 / Phase 1 bootstrap**.

Completed:

- repository created and mirror-pushed from `weekly-etf`;
- control layer rewritten to identify this as the EU/UCITS environment;
- EU authority files are being added;
- initial EU state separation is being introduced.

Not yet completed:

- EU workflow separation;
- EU output filename separation;
- UCITS pricing line support;
- verified UCITS symbol registry;
- Dutch-first EU report renderer;
- production delivery enablement.

## Current authority rules

1. U.S.-listed ETFs are **not** EU portfolio instruments.
2. U.S. ETFs may appear only as research proxies / benchmark comparators.
3. EU holdings must become UCITS ETFs with ISIN-first identity.
4. Dutch/EU investability requires UCITS status and PRIIPs/KID availability before funding.
5. The starting EU portfolio state is cash-only until instruments pass the UCITS investability contract.
6. Any existing cloned U.S. reports, pricing audits or portfolio entries are historical clone artifacts, not EU current-position truth.

## Current state files

The preferred EU files are:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
```

Temporary compatibility files may exist while the cloned runtime is refactored, but EU work should move toward the EU-specific names above.

## Stable inherited capabilities worth preserving

From `weekly-etf`, the EU repo should preserve:

- runtime-driven report state;
- persisted pricing audits;
- valuation history discipline;
- run manifests;
- delivery HTML validation;
- Dutch localization quality gates;
- ticker/link rendering discipline;
- state-derived equity curve;
- capital re-underwriting discipline;
- strict separation of state, report copy and delivery rendering.

## Current weaknesses

### 1. U.S. clone artifacts still exist

The repo currently inherits U.S. ETF output and state artifacts. They must not be mistaken for EU portfolio truth.

### 2. UCITS universe is not yet verified

The repo does not yet have a validated UCITS symbol registry with ISIN, exchange line, currency, TER, KID status and investability status.

### 3. Pricing still assumes the U.S. pipeline

Pricing code and workflows still need to be adapted to UCITS exchange tickers and trading currency lines.

### 4. Report output is not yet Dutch/EU-native

The inherited report is bilingual U.S.-ETF reporting. The EU report must become Dutch-client native, with UCITS/tradability disclosure and U.S. proxies clearly marked as research-only.

### 5. Delivery must remain blocked until EU validators pass

Do not send production EU emails until EU state, UCITS registry, no-U.S.-holding validation and output contracts pass.

## Immediate priority

Build the first safe EU separation layer:

1. Add UCITS control contracts.
2. Add UCITS config stubs.
3. Add cash-only EU state files.
4. Add validator blocking U.S.-listed ETFs as EU holdings.
5. Rename/disable production workflow until EU output contract is ready.

## Stable decision

The EU repo should not be a mechanical ticker replacement. It should be a separate UCITS investment-universe product using the proven runtime/reporting engine as scaffolding.
