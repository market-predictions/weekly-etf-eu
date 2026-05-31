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

The repo is in **Phase 3 — UCITS pricing-line preflight and candidate-report preparation**.

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
- generated EU markdown skeletons committed under `output/`;
- initial UCITS candidate registry seeded;
- UCITS symbol registry validator added;
- UCITS investability contract validator added;
- EU workflow now validates UCITS registry and investability contract;
- registry YAML syntax fix applied;
- UCITS registry validation run passed in GitHub Actions;
- UCITS pricing-line contract added;
- UCITS pricing candidate extractor added;
- UCITS pricing candidate validator added;
- non-authoritative UCITS pricing preflight added;
- UCITS pricing preflight validator added;
- EU workflow now runs and validates UCITS pricing-line preflight;
- UCITS pricing-line preflight validation passed in GitHub Actions;
- non-delivery pricing candidate and preflight artifacts are committed under `output/pricing/` by the workflow.

Not yet completed:

- valuation-grade UCITS pricing authority;
- verified pricing-source lineage beyond non-authoritative yfinance connectivity;
- funded EU model portfolio;
- Dutch-first production report renderer with real UCITS positions;
- production PDF/email delivery enablement.

## Latest validation result

The latest `Weekly ETF EU UCITS bootstrap validation` GitHub Actions run passed after adding the UCITS pricing-line preflight layer.

Validated markers now include:

```text
UCITS symbol registry validation
UCITS investability contract validation
UCITS pricing candidate extraction
UCITS pricing candidate validation
non-authoritative UCITS pricing preflight
UCITS pricing preflight validation
EU cash-only state validation
no U.S.-listed ETF appears as an EU holding
EU markdown report skeleton rendered
EU output contract passed
inherited U.S. production sender is disabled
no delivery is attempted
```

Generated non-delivery outputs include:

```text
output/weekly_etf_eu_review_260531.md
output/weekly_etf_eu_review_nl_260531.md
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
```

These artifacts are bootstrap/preflight outputs only. They are not production pricing authority and not a production report delivery receipt.

## Current UCITS registry status

The current registry is:

```text
config/ucits_symbol_registry.yml
```

Seed entries include:

```text
core_us_equity_cspx
semiconductor_vaneck_smh_ucits
gold_ishares_physical_gold_etc
infrastructure_ishares_global_infr
```

Current authority posture:

- `core_us_equity_cspx` is the only `verified_candidate_not_funded` seed and is eligible for non-authoritative pricing-line preflight.
- `semiconductor_vaneck_smh_ucits` remains `candidate_requires_verification` until domicile, distribution policy, replication method and pricing symbol are verified.
- `gold_ishares_physical_gold_etc` remains policy-blocked because it is an ETC, not a UCITS ETF.
- `infrastructure_ishares_global_infr` remains a placeholder requiring issuer confirmation.

No candidate is funded.

## Current pricing-line status

The first pricing-line phase is non-authoritative and cannot mutate portfolio state.

Current pricing-preflight rules:

- source of truth: `config/ucits_symbol_registry.yml`;
- eligible status: `verified_candidate_not_funded` only;
- output artifacts: `output/pricing/ucits_pricing_candidates_*.json` and `output/pricing/ucits_pricing_preflight_*.json`;
- authority flags: `portfolio_mutation=false`, `production_delivery=false`, `funding_authority=false`;
- pricing success does not promote candidates to `fundable`.

## Current authority rules

1. U.S.-listed ETFs are **not** EU portfolio instruments.
2. U.S. ETFs may appear only as research proxies / benchmark comparators.
3. EU holdings must become UCITS ETFs with ISIN-first identity.
4. Dutch/EU investability requires UCITS status and PRIIPs/KID availability before funding.
5. The starting EU portfolio state is cash-only until instruments pass the UCITS investability contract.
6. Pricing-line connectivity alone is not funding authority.
7. Any existing cloned U.S. reports, pricing audits or portfolio entries are historical clone artifacts, not EU current-position truth.

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

### 2. UCITS universe is only partially verified

The repo has an initial validated registry structure, but most candidates are not yet verified enough for pricing or funding.

### 3. Pricing is only a non-authoritative connectivity preflight

The first pricing-line layer uses non-authoritative connectivity tests. It is useful for validating symbols and plumbing, but not yet enough for valuation-grade report authority.

### 4. Report output is only a skeleton

The current EU report is a cash-only bootstrap skeleton. It is not yet a full Dutch/EU UCITS investment report.

### 5. Delivery remains blocked

Production delivery remains blocked until EU state, UCITS registry, valuation-grade UCITS pricing, no-U.S.-holding validation and output contracts pass.

## Immediate priority

Begin the UCITS candidate-report phase.

1. Extend the Dutch-first skeleton renderer to include a UCITS candidate table from `config/ucits_symbol_registry.yml`.
2. Surface pricing-preflight status as non-authoritative connectivity information only.
3. Keep portfolio state cash-only.
4. Add a validator that prevents pricing-preflight rows from being interpreted as funded positions.
5. Keep delivery disabled.

## Stable decision

The EU repo should not be a mechanical ticker replacement. It should be a separate UCITS investment-universe product using the proven runtime/reporting engine as scaffolding.
