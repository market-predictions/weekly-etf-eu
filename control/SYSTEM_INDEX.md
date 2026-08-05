# Weekly ETF EU Review OS — System Index

This file is the first entry point for serious work on `market-predictions/weekly-etf-eu`.

## Product purpose

```text
Dutch/EU-client ETF review using UCITS ETFs as investable instruments.
```

The upstream `market-predictions/weekly-etf` repository is a donor for mature implementation patterns. It is not authority for EU holdings, recipients, trading lines or delivery decisions.

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

1. **Decision framework** — which UCITS instruments deserve capital.
2. **Input/state contract** — authoritative instruments, prices, holdings, cash and ledger facts.
3. **Output contract** — Dutch-primary and English-companion report behavior.
4. **Operational runbook** — generation, validation, persistence, transport and closeout.
5. **Governance and release assurance** — independent proof that the complete requested outcome was achieved.

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

The canonical routine workflow must run the governance gate immediately before guarded transport:

- `.github/workflows/run-weekly-etf-eu-routine.yml`

## Cross-project governance authority

The canonical shared governance standard, adoption register, templates, and drift audit now live in the private repository:

```text
market-predictions/control-plane
```

Canonical standard:

```text
https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
```

The following local files remain as migration provenance and compatibility history, not current shared authority:

- `control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md`
- `control/CROSS_PROJECT_GOVERNANCE_ADOPTION_REGISTER.md`
- `control/PROJECT_GOVERNANCE_BOOTSTRAP_TEMPLATE.md`
- `control/PROJECT_PROMPT_GOVERNANCE_CLAUSE.md`
- `control/CROSS_PROJECT_GOVERNANCE_ROLLOUT_WORK_PACKAGE_20260805.md`
- `control/decisions/CROSS_PROJECT_GOVERNANCE_STANDARD_ADOPTION_DECISION_20260805.md`

ETF EU instrument, state, report, recipient, delivery, and portfolio authority remains local to this repository.

## Canonical EU control files

- `control/ETF_EU_PORTING_STRATEGY_DECISION_20260618.md`
- `control/UCITS_ETF_REVIEW_CONTRACT_V1.md`
- `control/UCITS_INVESTABILITY_RULES.md`
- `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md`
- `control/UCITS_MIGRATION_PLAN.md`
- `control/ETF_EU_PRODUCTION_DELIVERY_CLOSEOUT_CONTRACT_V1.md`
- `control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md`
- `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`

## Canonical EU configuration

- `config/ucits_symbol_registry.yml`
- `config/ucits_benchmark_proxy_map.yml`
- `config/nl_client_investability_rules.yml`
- `config/etf_eu_discovery_universe.yml`

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
4. never import U.S. state or recipient authority as EU authority.

## Non-negotiable controls

- Use ISIN-first identity; ticker alone is insufficient.
- Do not present U.S.-listed ETFs as Dutch/EU investable holdings.
- Do not fund an instrument before investability and pricing gates pass.
- Do not mutate portfolio state or ledger without explicit authority.
- Do not claim production delivery from generation, validation or SMTP success alone.
- Bind source SHA, run identity and report hashes before guarded transport.
- Require independent receipt evidence before `DELIVERY_CONFIRMED`.
- Treat missing or contradictory evidence as a blocker.
- Do not treat legacy workflow presence as proof of production authority.
- Do not require the user to coordinate implementation and assurance roles separately.

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
ROUTINE_WEEKLY_ETF_EU_PRODUCTION_WITH_INDEPENDENT_RELEASE_ASSURANCE
```

Current direction:

```text
fresh pricing and immutable run identity
→ authoritative portfolio/state contract
→ Dutch and English report generation
→ implementation validation
→ independent governance reconstruction and hash binding
→ guarded transport
→ independent receipt verification
→ production closeout
```
