# Weekly ETF EU Review OS — System Index

This file is the first entry point for serious work on `market-predictions/weekly-etf-eu`.

## Product purpose

```text
Dutch/EU-client Weekly ETF review using EU-investable UCITS ETFs and permitted ETCs.
```

The upstream `market-predictions/weekly-etf` repository is a donor for mature implementation patterns. It is not authority for EU holdings, recipients, trading lines, allocation decisions or delivery decisions.

## Mandatory session start

Read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`
5. `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`
6. the minimum relevant execution files

## Five-layer operating model

Always distinguish:

1. **Decision framework** — which UCITS instruments deserve capital and which allocation decision is authoritative.
2. **Input/state contract** — authoritative instruments, prices, holdings, shares, cash, ledger and decision lineage.
3. **Output contract** — Dutch-primary and English-companion report behavior.
4. **Operational runbook** — generation, validation, persistence, transport and closeout.
5. **Governance and release assurance** — independent proof that the complete requested outcome was achieved.

## Product boundary

This repository produces Weekly ETF EU reports only.

Current boundary authority:

- `control/REPOSITORY_PRODUCT_BOUNDARY.md`
- `tools/validate_etf_eu_repository_boundary.py`
- `.github/workflows/validate-etf-eu-repository-boundary.yml`

Active FX prediction runners, DailyTradeBias outputs, `daily_outputs`, `mt5_output`, `prediction.py` and `daily-fx` prompt surfaces are prohibited. Neutral data-provider use for bounded UCITS pricing diagnostics is not itself an FX product boundary violation.

## Allocation authority

Current release-policy authority:

- `config/etf_eu_portfolio_policy_v2.yml`
- `tools/validate_etf_eu_portfolio_policy.py`
- `output/etf_eu_portfolio_state.json`
- `output/etf_eu_trade_ledger.csv`
- `output/activation/etf_eu_stage1_allocation_decision_20260804_STAGE1_30947965670_1.json`

The active method is:

```text
protected_state_plus_explicit_authorized_mutation
```

For valuation-only runs, ticker identity, exact shares and cash are preserved. Any mutation requires a current explicit allocation decision. Portfolio concentration is an underwriting observation unless a separately approved policy establishes a hard limit.

No universal 50% maximum position or mandatory cash floor is currently authorized. The Weekly ETF donor's 75% threshold is pricing coverage, not position sizing.

## Two-role governance model

The project has one user-facing coordinator and two internally separated roles:

```text
implementation_operations
governance_release_assurance
```

Role A builds or repairs a release candidate. Role B independently reconstructs and certifies or rejects it. Role A may not self-certify. Role B may not mutate the candidate it certifies.

Project authority files:

- `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`
- `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`
- `control/ETF_EU_GOVERNANCE_RELEASE_ASSURANCE_WORK_PACKAGE_20260805.md`
- `control/ETF_EU_GOVERNANCE_CHANGELOG.md`

Machine controls:

- `tools/build_etf_eu_release_assurance.py`
- `tools/validate_etf_eu_release_assurance.py`
- `.github/workflows/validate-etf-eu-release-assurance.yml`

The eventual canonical routine workflow must run the governance gate immediately before guarded transport. During the current remediation, no workflow has transport authority merely because it can render or package a report.

## Cross-project governance authority

The canonical shared governance standard, adoption register, templates and drift audit live in the private repository:

```text
market-predictions/control-plane
```

Canonical standard:

```text
https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
```

Local cross-project files remain migration provenance and compatibility history, not current shared authority. ETF EU instrument, state, report, recipient, delivery and portfolio authority remains local.

## Canonical EU control files

- `control/ETF_EU_PORTING_STRATEGY_DECISION_20260618.md`
- `control/UCITS_ETF_REVIEW_CONTRACT_V1.md`
- `control/UCITS_INVESTABILITY_RULES.md`
- `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md`
- `control/UCITS_MIGRATION_PLAN.md`
- `control/ETF_EU_PRODUCTION_DELIVERY_CLOSEOUT_CONTRACT_V1.md`
- `control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md`
- `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`
- `control/REPOSITORY_PRODUCT_BOUNDARY.md`
- `control/ETF_EU_MATURITY_GAP_REVIEW_2026-08-06.md`

## Canonical EU configuration

- `config/ucits_symbol_registry.yml`
- `config/ucits_benchmark_proxy_map.yml`
- `config/nl_client_investability_rules.yml`
- `config/etf_eu_discovery_universe.yml`
- `config/etf_eu_portfolio_policy_v2.yml`

## Canonical EU state

- `output/etf_eu_portfolio_state.json`
- `output/etf_eu_valuation_history.csv`
- `output/etf_eu_trade_ledger.csv`
- `output/etf_eu_recommendation_scorecard.csv`

Compatibility files from inherited repositories are not authority unless a current EU contract explicitly imports them.

## Upstream-first reuse rule

Before creating or materially changing an EU workflow, runtime script, validator, renderer or control contract:

1. inspect the closest mature upstream implementation;
2. choose port, adapt, wrap or intentional divergence;
3. record the decision;
4. never import U.S. state, allocation or recipient authority as EU authority;
5. never copy unrelated product runners or output paths merely because they exist upstream.

## Non-negotiable controls

- Use ISIN-first identity; ticker alone is insufficient.
- Do not present U.S.-listed ETFs as Dutch/EU investable holdings.
- Do not fund an instrument before investability and pricing gates pass.
- Do not mutate portfolio state, shares, cash or ledger without explicit authority.
- Do not claim production delivery from generation, validation or SMTP success alone.
- Bind source SHA, run identity, protected-state lineage, decision identity and report hashes before guarded transport.
- Require independent receipt evidence before `DELIVERY_CONFIRMED`.
- Treat missing or contradictory evidence as a blocker.
- Do not treat legacy workflow presence as proof of production authority.
- Do not require the user to coordinate implementation and assurance roles separately.
- Do not run or surface Weekly FX outputs from this repository.

## Run verification discipline

When the coordinator triggers a GitHub Actions run, the coordinator owns the verification loop:

1. resolve the run and commit SHA;
2. inspect workflow and job status;
3. inspect the exact failing step and logs;
4. verify generated artifacts and manifests;
5. run independent governance assurance;
6. verify transport and receipt evidence;
7. report the precise terminal state.

The user is not the default workflow monitor.

## Current operating mode

```text
CLIENT_GRADE_RELEASE_REMEDIATION_NO_SEND
```

Current direction:

```text
product-boundary PASS
→ protected-state allocation-lineage PASS
→ fresh completed-close pricing
→ Dutch and English candidate generation
→ implementation validation
→ visual review
→ user review
→ independent governance reconstruction and hash binding
→ guarded transport
→ independent receipt verification
→ production closeout
```
