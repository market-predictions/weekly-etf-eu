# Weekly ETF EU Repo Bootstrap

Target repo: `market-predictions/weekly-etf-eu`
Source repo: `market-predictions/weekly-etf`

## Decision

Create a separate EU / UCITS ETF review repo instead of mutating the existing U.S.-ETF review repo.

The current `weekly-etf` repo remains the U.S.-ETF model baseline. The new `weekly-etf-eu` repo becomes the European / Dutch-client UCITS ETF model.

## Why separate

This is not a translation change. The EU model changes the investable universe, state contract, instrument identity, pricing identifiers, report copy, and validation rules.

## Manual prerequisite

The target repo does not currently exist and must be created outside this connector first:

```bash
git clone --bare git@github.com:market-predictions/weekly-etf.git
cd weekly-etf.git
git push --mirror git@github.com:market-predictions/weekly-etf-eu.git
cd ..
rm -rf weekly-etf.git
```

## First files to add after clone

```text
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
control/UCITS_INVESTABILITY_RULES.md
control/UCITS_SYMBOL_REGISTRY_CONTRACT.md
control/UCITS_MIGRATION_PLAN.md
config/etf_eu_discovery_universe.yml
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
config/nl_client_investability_rules.yml
```

## Core authority rules for the EU repo

1. EU portfolio instruments must be UCITS ETFs.
2. U.S. ETFs may be used only as research benchmarks or proxy references.
3. Canonical instrument identity should be ISIN-first, not ticker-first.
4. The EU repo must use its own portfolio state, valuation history, trade ledger, recommendation scorecard, pricing audits, runtime files and report outputs.
5. The Dutch report should be Dutch-client native, not merely a translation of the U.S. report.
6. Production send should remain blocked until EU-specific validators pass.

## Seed state approach

Start cash-only until UCITS instruments have passed the investability contract:

```json
{
  "schema_version": "etf_eu_portfolio_state_v1",
  "base_currency": "EUR",
  "cash_eur": 100000.0,
  "positions": [],
  "notes": [
    "Initial EU/UCITS model state.",
    "U.S.-listed ETFs are research proxies only, not EU portfolio holdings."
  ]
}
```

## First validators

```text
tools/validate_ucits_investability_contract.py
tools/validate_ucits_symbol_registry.py
tools/validate_no_us_etf_as_eu_holding.py
tools/validate_etf_eu_output_contract.py
```

## First implementation phases

1. Create and mirror `weekly-etf-eu`.
2. Rewrite control files for EU authority.
3. Add UCITS contracts and registry configs.
4. Replace U.S. portfolio state with EU cash-only seed state.
5. Add no-U.S.-ETF-as-holding validator.
6. Rename workflow and run queue to EU-specific names.
7. Convert pricing to UCITS exchange tickers and trading currency lines.
8. Render Dutch-first EU report with UCITS/tradability disclosure.

## Do not do

Do not mechanically replace U.S. tickers with EU tickers.
Do not reuse the U.S. portfolio state as EU portfolio truth.
Do not claim EU report delivery is production-ready before EU validators pass.
