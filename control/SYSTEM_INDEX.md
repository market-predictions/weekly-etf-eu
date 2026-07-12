# Weekly ETF EU Review OS — System Index

This file is the first entry point for serious work on the `weekly-etf-eu` system.

## Purpose

This repository is the European / Dutch-client UCITS ETF review environment derived from `market-predictions/weekly-etf`.

It must not be treated as a translated copy of the U.S.-ETF model. The current product goal is:

```text
Dutch/EU-client ETF review using UCITS ETFs as investable instruments.
```

The original `market-predictions/weekly-etf` repository remains the U.S.-ETF model baseline and upstream donor for mature implementation layers.

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

## Upstream-first reuse rule

For every new ETF EU task, work package, workflow change, runtime script, validator, renderer, delivery step, or control file, inspect `market-predictions/weekly-etf` before designing or implementing the EU change.

Required discipline:

1. Identify the closest mature upstream concept, script, workflow step, validator, manifest, or runbook in `market-predictions/weekly-etf`.
2. Decide explicitly whether to port as-is, adapt, wrap, or intentionally diverge.
3. Record the reason for adaptation or divergence in the work package, decision artifact, commit summary, or final response.
4. Borrow implementation concepts, contracts, evidence patterns, and operational safeguards before creating new EU-specific machinery.
5. Never port U.S. portfolio state, U.S. holdings, U.S. instrument authority, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

Do not reinvent an EU component from scratch until the upstream `weekly-etf` equivalent has been checked.

## Canonical EU control files

- `control/ETF_EU_PORTING_STRATEGY_DECISION_20260618.md` — stable decision to keep `weekly-etf-eu` as EU source-of-truth and use `weekly-etf` only as an upstream donor for mature report/runtime/bilingual/macro/delivery safeguards.
- `control/UCITS_ETF_REVIEW_CONTRACT_V1.md` — authority contract for the EU/UCITS ETF review product.
- `control/UCITS_INVESTABILITY_RULES.md` — Dutch/EU investability rules for UCITS, PRIIPs/KID, trading line, liquidity and disclosure.
- `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md` — ISIN-first instrument identity and proxy/candidate separation.
- `control/UCITS_MIGRATION_PLAN.md` — staged migration and donor-port roadmap from the cloned U.S.-ETF codebase to the EU/UCITS model.
- `control/ETF_EU_PRODUCTION_DELIVERY_CLOSEOUT_CONTRACT_V1.md` — evidence requirements for closing a production delivery cycle.
- `control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md` — the authoritative operational runbook for fresh generation, validation, guarded delivery, delayed receipt verification and production closeout of routine Weekly ETF EU reports.

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
- Port mature behavior from `weekly-etf`; do not port U.S. assumptions as EU authority.
- Check the upstream `market-predictions/weekly-etf` implementation before creating or materially changing EU tasks, scripts, validators, workflows, renderers, delivery files, or control files.

## GitHub run verification discipline

When ChatGPT triggers a GitHub Actions run or any run-queue workflow, ChatGPT owns the verification loop by default.

Operational rule:

1. Trigger the run by committing the queue/control file.
2. Build in a short pause before the first status check so GitHub has time to create the workflow run.
3. Poll run status through available GitHub tools and artifact commits; do not conclude from an immediate empty result.
4. Check GitHub Actions, commit status, workflow jobs, logs and generated artifact commits directly from GitHub where tool access allows.
5. If the run fails, inspect the failing step/logs and patch the repo before asking the user for manual screenshots.
6. If the run passes, verify the committed output artifacts, manifests or receipts before claiming success.
7. Ask the user for an Actions screenshot only when GitHub tool access cannot expose the run, job logs, artifact, or permission state.

Never rely on the user as the default run-status checker when GitHub tool access is available.

## Current operating mode

```text
ROUTINE_WEEKLY_ETF_EU_PRODUCTION
```

The production-enablement cycle is closed. New weekly reports follow:

```text
control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
```

Current direction of travel:

```text
keep weekly-etf-eu as EU/UCITS source-of-truth
→ use weekly-etf as upstream donor for mature implementation layers
→ create a fresh run id, report date and suffix for every routine report
→ use current pricing, EU state and ISIN-first instrument authority
→ generate and validate Dutch-primary and English-companion outputs
→ execute guarded current-package delivery
→ perform delayed independent receipt verification
→ create routine manifest and production closeout
→ create architecture packages only for specific defects or material capability changes
```
