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

The repo is in **Phase 4 — UCITS valuation-pricing authority scaffolding validated; valuation-source integration still pending**.

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
- non-delivery pricing candidate and preflight artifacts are committed under `output/pricing/` by the workflow;
- Dutch-first candidate-report table added to the renderer;
- candidate-report validator added;
- EU workflow now validates the candidate-report layer;
- candidate-report validation passed in GitHub Actions;
- UCITS valuation-pricing authority contract added;
- UCITS pricing source policy added;
- valuation-price artifact builder added;
- valuation-price artifact validator added;
- EU workflow now builds and validates the valuation-price artifact;
- Phase 4 valuation-pricing validation run passed in GitHub Actions;
- valuation-price artifact committed under `output/pricing/`.

Not yet completed:

- integration of a live authoritative valuation source such as exchange-official close or verified Twelve Data line;
- verified pricing-source lineage beyond non-authoritative yfinance connectivity;
- any `valuation_grade: true` UCITS price row;
- candidate promotion path from `verified_candidate_not_funded` to `fundable`;
- funded EU model portfolio;
- Dutch-first production report renderer with real UCITS positions;
- production PDF/email delivery enablement.

## Latest validation result

The latest `Weekly ETF EU UCITS bootstrap validation` GitHub Actions run passed after adding the Phase 4 valuation-pricing layer.

Validated markers now include:

```text
UCITS symbol registry validation
UCITS investability contract validation
UCITS pricing candidate extraction
UCITS pricing candidate validation
non-authoritative UCITS pricing preflight
UCITS pricing preflight validation
UCITS valuation-pricing source policy validation
UCITS valuation-price artifact build
UCITS valuation-price artifact validation
EU cash-only state validation
no U.S.-listed ETF appears as an EU holding
EU candidate report skeleton rendered
EU output contract passed
EU candidate-report contract passed
inherited U.S. production sender is disabled
no delivery is attempted
```

Generated non-delivery outputs include:

```text
output/weekly_etf_eu_review_260531.md
output/weekly_etf_eu_review_nl_260531.md
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
output/pricing/ucits_valuation_prices_*.json
```

Latest valuation artifact observed:

```text
output/pricing/ucits_valuation_prices_20260531_133912.json
```

This artifact is valuation-authority scaffolding only. It contains pending valuation rows and explicitly keeps:

```text
portfolio_mutation=false
production_delivery=false
funding_authority=false
valuation_grade_row_count=0
```

It is not a production pricing authority artifact, not a portfolio valuation-history mutation and not a production report delivery receipt.

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

- `core_us_equity_cspx` is the only `verified_candidate_not_funded` seed and is eligible for non-authoritative pricing-line preflight and Phase 4 valuation-price pending rows.
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

## Current valuation-pricing status

The valuation-pricing layer is now present and validated as a non-mutating authority scaffold.

Current valuation-pricing files:

```text
control/UCITS_VALUATION_PRICING_CONTRACT_V1.md
config/ucits_pricing_source_policy.yml
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
output/pricing/ucits_valuation_prices_*.json
```

Current source-policy posture:

- `exchange_official` is the preferred valuation source but not yet integrated;
- `twelve_data` is a candidate valuation source pending symbol/date/currency verification per UCITS trading line;
- `issuer_factsheet` is reference/stale-check only;
- `yahoo_yfinance` remains non-authoritative connectivity only.

Current artifact behavior:

- CSPX London and SXR8 Xetra rows are present as `valuation_grade_pending`;
- non-authoritative yfinance evidence is preserved inside `non_authoritative_preflight_evidence`;
- yfinance evidence is explicitly excluded from valuation authority under current policy;
- `valuation_grade_row_count=0`;
- no state mutation, funding authority, PDF generation or email delivery occurs.

## Current report-surface status

The Dutch-first and English companion reports now include a UCITS candidate registry table.

Current report-surface rules:

- the candidate table is not a portfolio;
- the candidate table is not a buy recommendation;
- the candidate table is not valuation authority;
- every candidate row remains not funded;
- pricing-preflight status is non-authoritative connectivity only;
- valuation-pricing artifact status is not funding authority;
- U.S. proxies remain research-only.

## Current authority rules

1. U.S.-listed ETFs are **not** EU portfolio instruments.
2. U.S. ETFs may appear only as research proxies / benchmark comparators.
3. EU holdings must become UCITS ETFs with ISIN-first identity.
4. Dutch/EU investability requires UCITS status and PRIIPs/KID availability before funding.
5. The starting EU portfolio state is cash-only until instruments pass the UCITS investability contract.
6. Pricing-line connectivity alone is not funding authority.
7. Valuation-price artifact generation alone is not funding authority.
8. Candidate-report visibility alone is not portfolio authority.
9. Any existing cloned U.S. reports, pricing audits or portfolio entries are historical clone artifacts, not EU current-position truth.

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

The current non-delivery EU candidate report skeleton files are:

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

### 3. Pricing source authority is still pending

The repo now has valuation-pricing scaffolding, but no integrated authoritative completed-session close source yet. Current yfinance evidence is deliberately preserved as connectivity-only and excluded from valuation authority.

### 4. Report output is still a bootstrap candidate report

The current EU report shows cash-only portfolio state and candidate rows. It is not yet a full Dutch/EU UCITS investment report.

### 5. Delivery remains blocked

Production delivery remains blocked until EU state, UCITS registry, valuation-grade UCITS pricing, no-U.S.-holding validation and output contracts pass.

## Immediate priority

Move from valuation-pricing scaffolding to real valuation-source integration.

1. Decide whether the first valuation-grade source integration should be Twelve Data or exchange-official close.
2. Define exact provider symbols and currency evidence for CSPX London and SXR8 Xetra.
3. Implement source-specific fetch logic without mutating portfolio state.
4. Keep yfinance as non-authoritative connectivity/research preflight unless explicitly promoted.
5. Keep portfolio state cash-only and delivery disabled.

## Stable decision

The EU repo should not be a mechanical ticker replacement. It should be a separate UCITS investment-universe product using the proven runtime/reporting engine as scaffolding.
