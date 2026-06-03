# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-06-04

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

This repo is intended to become:

```text
market-predictions/weekly-etf-eu = UCITS ETF model for Dutch/EU clients
```

The clone still contains many U.S.-ETF artifacts, old workflow names and historical outputs. Those files are inherited history, not final EU authority.

## Current migration status

The repo is in **Phase 5 — M1 typed pricing spine integrated; source metadata and agreement gate next**.

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
- valuation-price artifact committed under `output/pricing/`;
- parallel pricing-spine workstream plan and instruction files added;
- M0 ground-clearing PR merged: repository README added, archive/quarantine notes added, local clutter `.gitignore` added, and bootstrap/runtime dependencies pinned in `requirements.txt`;
- `control/CHANGELOG.md` added for integration-level tracking;
- M1 common `PriceSource` / `PriceResult` interface integrated;
- M1 Stooq pricing adapter integrated;
- M1 Börse Frankfurt / Xetra pricing adapter integrated;
- M1 Yahoo fallback pricing adapter integrated;
- M1 issuer NAV reference adapter integrated;
- at least two fixture-backed provider adapters now return typed `PriceResult` evidence or typed unresolved rows;
- the repo now has a typed multi-source pricing evidence spine.

Not yet completed:

- source metadata policy integration;
- agreement gate integration;
- valuation artifact consumption of agreement-gate output;
- integration of a live authoritative valuation source such as exchange-official close or verified Twelve Data line;
- verified pricing-source lineage beyond current adapter evidence;
- any `valuation_grade: true` UCITS price row;
- candidate promotion path from `verified_candidate_not_funded` to `fundable`;
- funded EU model portfolio;
- Dutch-first production report renderer with real UCITS positions;
- production PDF/email delivery enablement.

## Latest integration result

M0 ground-clearing was merged on 2026-06-03 as commit:

```text
c1476171606206d369190bf4c8cf126222a1e753
```

The M1 pricing-spine PRs were then merged into `main`:

| PR | Integrated workstream | Merge commit |
|---|---|---|
| `#3` | common pricing interface | `0c21629aa315f18a0ebceb0a301841d457d2a554` |
| `#4` | Stooq pricing adapter | `c92cff7a973f27f152b4c866515d7c84e28135d6` |
| `#5` | Börse Frankfurt / Xetra pricing adapter | `34d6c909e87015de49e31ed3fc25294084faad16` |
| `#6` | Yahoo fallback pricing adapter | `9138efd0d5613527bd6ab6f44313596e6cb6907f` |
| `#7` | issuer NAV reference adapter | `7b74a36de88b8fdb5b4a4f8709312df533c27a9d` |

Authority boundaries after these merges remain:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

The M1 PRs reported fixture-backed local test results in their PR descriptions, but no production delivery or valuation-grade workflow is claimed from those merges.

## Current parallel pricing-spine status

The parallel pricing-spine integration has completed the M1 interface and adapter layer.

Current integration state:

- M0 ground-clearing is integrated.
- Common pricing interface is integrated.
- Stooq adapter is integrated.
- Börse Frankfurt / Xetra adapter is integrated.
- Yahoo fallback adapter is integrated.
- Issuer NAV reference adapter is integrated.
- Source metadata policy is the next immediate integration target.
- Agreement gate integration is now technically unblocked by adapter availability, but should follow source metadata policy alignment.
- First report pricing-surface integration must wait until agreement-gate output exists.

Current pricing-spine target:

```text
PriceSource adapter interface
PriceResult typed result
source policy driven ordering
license_class as first-class metadata
agreement gate before valuation_grade
Yahoo as tertiary/provisional fallback, not sole valuation authority
```

## Integrated M1 pricing-spine details

### Common interface

Integrated files:

```text
pricing/README.md
pricing/price_result_schema.py
pricing/source_selection.py
pricing/sources/__init__.py
pricing/sources/base.py
tests/fixtures/pricing/fake_price_rows.json
tests/test_pricing_interface.py
```

Contract:

```text
PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult
```

Key shared concepts:

```text
PriceIdentity
PriceRequest
PriceResult
SourceLineage
status constants
license_class constants
authority_tier constants
```

### Stooq adapter

Integrated files:

```text
pricing/sources/stooq.py
config/source_symbol_overrides/stooq.yml
tests/test_stooq_adapter.py
tests/fixtures/pricing/stooq/cspx_daily.csv
tests/fixtures/pricing/stooq/no_data.csv
```

Role:

```text
provisional / cross-check source
license_class=provider_free_personal
authority_tier=diagnostic_candidate_source
```

Stooq mappings such as `CSPX London USD -> cspx.uk` and `SXR8 Xetra EUR -> sxr8.de` remain provisional and require provider coverage verification before valuation use.

### Börse Frankfurt / Xetra adapter

Integrated files:

```text
config/source_symbol_overrides/boerse_frankfurt.yml
pricing/sources/boerse_frankfurt.py
tests/fixtures/pricing/boerse_frankfurt/currency_uncertain.json
tests/fixtures/pricing/boerse_frankfurt/no_close.json
tests/fixtures/pricing/boerse_frankfurt/resolved_close.json
tests/test_boerse_frankfurt_adapter.py
```

Role:

```text
exchange-candidate evidence only
license_class=unknown
license_note=undocumented_free_source_pending_license_review
authority_tier=diagnostic_candidate_source
authority_note=exchange_candidate_evidence_only_not_valuation_authority
```

The endpoint is undocumented/free and pending source/license review. It must not become valuation authority by itself.

### Yahoo adapter

Integrated files:

```text
pricing/sources/yahoo.py
tests/test_yahoo_adapter.py
tests/fixtures/pricing/yahoo/cspx_history.json
tests/fixtures/pricing/yahoo/empty_history.json
tests/fixtures/pricing/yahoo/missing_close_history.json
```

Role:

```text
fallback / provisional evidence only
source_id=yahoo_yfinance
license_class=provider_free_personal
authority_tier=non_authoritative_connectivity_only
```

Yahoo/yfinance must not be the only path to valuation-grade UCITS pricing.

### Issuer NAV adapter

Integrated files:

```text
pricing/sources/issuer_nav.py
tests/test_issuer_nav_adapter.py
tests/fixtures/pricing/issuer_nav/valid_cspx_nav.json
tests/fixtures/pricing/issuer_nav/missing_currency_nav.json
```

Role:

```text
reference / stale-check evidence only
value_type=issuer_nav_reference
not_exchange_trading_line_close=true
license_class=issuer_public
authority_tier=diagnostic_candidate_source
```

Issuer NAV is not an exchange EOD close adapter and must not count as an independent market-close source for valuation-grade agreement.

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

The valuation-pricing layer is present and validated as a non-mutating authority scaffold.

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
- `yahoo_yfinance` remains non-authoritative connectivity only until the pricing-spine and agreement-gate policy explicitly change its role.

Current artifact behavior:

- CSPX London and SXR8 Xetra rows are present as `valuation_grade_pending`;
- non-authoritative yfinance evidence is preserved inside `non_authoritative_preflight_evidence`;
- yfinance evidence is explicitly excluded from valuation authority under current policy;
- `valuation_grade_row_count=0`;
- no state mutation, funding authority, PDF generation or email delivery occurs.

## Current report-surface status

The Dutch-first and English companion reports include a UCITS candidate registry table.

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
10. Yahoo/yfinance must not become the only path to valuation-grade UCITS pricing.
11. Issuer NAV is reference/stale-check evidence only, not market-close agreement evidence.
12. Valuation-grade status must come after source policy and agreement-gate conditions pass.
13. Pricing adapters return evidence; they do not mutate portfolio state, promote candidates, render reports, generate PDFs, send email, or produce delivery receipts.

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

The repo currently inherits U.S. ETF output and state artifacts. They must not be mistaken for EU portfolio truth. M0 has documented archive/quarantine policy, but has not moved inherited files yet.

### 2. UCITS universe is only partially verified

The repo has an initial validated registry structure, but most candidates are not yet verified enough for pricing or funding.

### 3. Pricing source authority is still pending

The repo now has a typed multi-source pricing evidence spine, but no integrated authoritative completed-session close source and no agreement-gated valuation-grade output yet.

### 4. Source metadata policy is not yet integrated

The next step is to integrate a deterministic source metadata register so pricing evidence can be filtered and interpreted by policy rather than hardcoded assumptions.

### 5. Agreement gate is not yet integrated

The repo has enough adapter availability to start agreement-gate work after source metadata alignment, but the gate does not yet classify rows as valuation-grade, provisional or blocked.

### 6. Report output is still a bootstrap candidate report

The current EU report shows cash-only portfolio state and candidate rows. It is not yet a full Dutch/EU UCITS investment report.

### 7. Delivery remains blocked

Production delivery remains blocked until EU state, UCITS registry, valuation-grade UCITS pricing, no-U.S.-holding validation and output contracts pass, and until a delivery receipt/manifest path exists.

## Immediate priority

Move from the integrated typed pricing evidence spine to a policy-governed valuation path.

1. Integrate source metadata policy.
2. Integrate agreement gate after source metadata policy alignment.
3. Wire agreement-gate output into valuation artifacts only after the coordinator confirms the gate is ready.
4. Add a first report pricing surface only after agreement-gate output exists.
5. Keep yfinance as non-authoritative connectivity/research preflight unless explicitly promoted by policy and agreement gates.
6. Keep issuer NAV as reference/stale-check evidence only.
7. Keep portfolio state cash-only and delivery disabled.

## Stable decision

The EU repo should not be a mechanical ticker replacement. It should be a separate UCITS investment-universe product using the proven runtime/reporting engine as scaffolding.

The current pricing architecture decision is: maintain a typed multi-source pricing spine first, then allow an agreement gate to classify prices as valuation-grade, provisional or blocked. Yahoo/yfinance can be useful as a tertiary/provisional fallback, but must not be the only route to valuation-grade UCITS pricing. Issuer NAV can support stale-check/reference context, but it is not an exchange market-close agreement source.