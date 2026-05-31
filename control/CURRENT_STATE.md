# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-05-31

## What this repository currently is

This repository has been cloned from `market-predictions/weekly-etf` into:

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

The clone still contains many U.S.-ETF artifacts, old workflow names and historical outputs. Those files are inherited history, not final EU authority.

## Current migration status

The repo is in **Phase 2 / Phase 3 transition**.

Completed:

- repository created and mirror-pushed from `weekly-etf`;
- control layer rewritten to identify this as the EU/UCITS environment;
- UCITS authority files added;
- EU config stubs added;
- EU cash-only state files added;
- `tools/validate_no_us_etf_as_eu_holding.py` added;
- inherited U.S. production send workflow disabled;
- EU bootstrap validation workflow added;
- first EU bootstrap validation run passed in GitHub Actions;
- EU output contract added;
- Dutch-first / English companion cash-only report skeleton renderer added;
- EU output contract validator added;
- output validator markdown-normalization fix added;
- normalized EU output-contract validation passed in GitHub Actions;
- generated EU markdown skeletons committed under `output/`.

Not yet completed:

- verified UCITS symbol registry;
- UCITS pricing line support;
- funded EU model portfolio;
- Dutch-first production report renderer with real UCITS positions;
- production PDF/email delivery enablement.

## Latest validation result

The latest `Weekly ETF EU UCITS bootstrap validation` GitHub Actions run passed.

Validated markers:

```text
EU control files exist
EU config files exist
EU cash-only state exists
no U.S.-listed ETF appears as an EU holding
EU markdown report skeleton rendered
EU output contract passed
inherited U.S. production sender is disabled
no delivery is attempted
```

Generated non-delivery outputs:

```text
output/weekly_etf_eu_review_260531.md
output/weekly_etf_eu_review_nl_260531.md
```

These reports show:

- cash-only bootstrap;
- no funded UCITS holdings;
- U.S. ETFs labelled as research proxies only;
- UCITS candidates requiring ISIN, KID/PRIIPs and trading-line verification;
- production delivery disabled.

This is a bootstrap validation and report-skeleton commit only. It is not a production report delivery receipt.

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

## Current output files

The current non-delivery EU report skeleton files are:

```text
output/weekly_etf_eu_review_260531.md
output/weekly_etf_eu_review_nl_260531.md
```

The Dutch file is the primary EU client-facing skeleton. The English file is a companion/operator-facing skeleton during bootstrap.

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

### 4. Report output is only a skeleton

The current EU report is a cash-only bootstrap skeleton. It is not yet a full Dutch/EU UCITS investment report.

### 5. Delivery remains blocked

Production delivery remains blocked until EU state, UCITS registry, UCITS pricing, no-U.S.-holding validation and output contracts pass.

## Immediate priority

Begin Phase 3: build and validate an initial UCITS candidate registry.

1. Identify candidate UCITS ETFs by theme.
2. Verify ISIN, provider, exchange ticker, exchange, trading currency, TER, UCITS status and PRIIPs/KID status.
3. Keep candidates as `candidate_requires_verification` until checked.
4. Only after registry validation, add UCITS pricing-line tests.

## Stable decision

The EU repo should not be a mechanical ticker replacement. It should be a separate UCITS investment-universe product using the proven runtime/reporting engine as scaffolding.
