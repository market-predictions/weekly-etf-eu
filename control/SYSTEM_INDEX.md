# Weekly ETF EU Review OS — System Index

This file is the first entry point for serious work on the `weekly-etf-eu` system.

## Purpose

This repository is the European / Dutch-client UCITS ETF review environment derived from `market-predictions/weekly-etf`.

It must not be treated as a translated copy of the U.S.-ETF model. The current product goal is:

```text
Dutch/EU-client ETF review using UCITS ETFs as investable instruments.
```

The original `market-predictions/weekly-etf` repository remains the U.S.-ETF model baseline.

## Four-layer operating model

Always distinguish:

1. **Decision framework** — which UCITS ETFs available to Dutch/EU investors deserve capital.
2. **Input/state contract** — where authoritative UCITS instrument, pricing, portfolio and investability facts come from.
3. **Output contract** — how Dutch-first EU client reports distinguish investable UCITS ETFs from U.S. research proxies.
4. **Operational runbook** — how GitHub Actions and scripts execute pricing, validation, rendering, state refresh and delivery without accidentally using U.S. ETF holdings as EU portfolio truth.

## Session start rule

For ETF EU architecture, debugging, prompt, workflow, state, pricing, discovery, localization or delivery work, read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution files

## Canonical EU control files

- `control/UCITS_ETF_REVIEW_CONTRACT_V1.md` — authority contract for the EU/UCITS ETF review product.
- `control/UCITS_INVESTABILITY_RULES.md` — Dutch/EU investability rules for UCITS, PRIIPs/KID, trading line, liquidity and disclosure.
- `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md` — ISIN-first instrument identity and proxy/candidate separation.
- `control/UCITS_MIGRATION_PLAN.md` — staged migration from the cloned U.S.-ETF codebase to the EU/UCITS model.

## Canonical EU config files

- `config/ucits_symbol_registry.yml` — ISIN-first registry for UCITS ETFs and exchange lines.
- `config/ucits_benchmark_proxy_map.yml` — U.S. proxy / benchmark to UCITS candidate mapping.
- `config/nl_client_investability_rules.yml` — client-facing Dutch/EU investability assumptions.
- `config/etf_eu_discovery_universe.yml` — EU/UCITS investable discovery universe.

## Canonical EU state files

Preferred EU-specific state files:

- `output/etf_eu_portfolio_state.json`
- `output/etf_eu_valuation_history.csv`
- `output/etf_eu_trade_ledger.csv`
- `output/etf_eu_recommendation_scorecard.csv`

Compatibility files from the U.S. clone may remain temporarily, but they are not EU authority unless explicitly rewritten to the EU cash-only seed state.

## Non-negotiable discipline

- Do not destructively mutate the U.S. `weekly-etf` repo for the EU model.
- Do not present U.S.-listed ETFs as investable holdings for Dutch/EU retail clients.
- U.S. ETFs may appear only as research proxies, benchmark comparators or thematic references.
- Use ISIN-first identity for UCITS ETFs; ticker alone is not enough.
- Do not fund a UCITS ETF before UCITS status, PRIIPs/KID availability, trading line and pricing are validated.
- Do not reuse the U.S. portfolio state as EU portfolio truth.
- Do not claim EU report production delivery until EU-specific validators pass and a delivery receipt or manifest exists.
- Keep decision framework, input/state contract, output contract and runbook separate.

## GitHub run verification discipline

When ChatGPT triggers a GitHub Actions run or any run-queue workflow, ChatGPT owns the verification loop by default.

Operational rule:

1. Trigger the run by committing the queue/control file.
2. Check GitHub Actions, commit status, workflow jobs, logs and generated artifact commits directly from GitHub where tool access allows.
3. If the run fails, inspect the failing step/logs and patch the repo before asking the user for manual screenshots.
4. If the run passes, verify the committed output artifacts, manifests or receipts before claiming success.
5. Ask the user for an Actions screenshot only when GitHub tool access cannot expose the run, job logs, artifact, or permission state.

Never rely on the user as the default run-status checker when GitHub tool access is available.

## Current direction of travel

The EU repo is in bootstrap/migration mode:

```text
clone baseline
→ freeze U.S. state as non-authoritative
→ add UCITS control contracts
→ add ISIN-first registry
→ seed EU cash-only state
→ add no-U.S.-ETF-as-holding validator
→ rename workflow/run queue/output files
→ price UCITS trading lines
→ render Dutch-first EU report
→ only then enable production delivery
```
