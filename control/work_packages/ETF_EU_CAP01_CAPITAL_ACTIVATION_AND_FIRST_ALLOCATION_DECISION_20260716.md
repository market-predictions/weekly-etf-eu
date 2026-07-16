# ETF-EU-CAP01 — Capital activation and first allocation decision

## Layer

```text
decision framework + input/state contract + output contract + operational runbook
```

## Current issue

The production report can identify, price and compare UCITS candidates but always ends with `retain_cash_pending_separate_allocation_decision`. The model portfolio therefore remains at EUR 100,000 cash even when a verified implementation line exists.

## Root cause

No EU-specific allocation decision artifact, whole-share sizing engine, guarded model-capital authority or portfolio-state mutation path exists.

## Donor inspection

Inspected in `market-predictions/weekly-etf`:

- `runtime/build_etf_report_state.py`;
- `runtime/model_execution_engine.py`;
- `runtime/model_execution_guarded_auto.py`;
- `runtime/finalize_executed_etf_report.py`;
- `tools/validate_etf_model_execution.py`.

Adapted concepts:

- official portfolio state remains quantity authority;
- decision and execution artifacts are separate;
- hard policy gates precede mutation;
- trade ledger provides idempotency and auditability;
- post-execution report is rebuilt from official state.

Intentional EU divergences:

- canonical identity is ISIN plus exact trading line, not ticker alone;
- whole shares only;
- cash is actually debited or credited;
- blocked target capacity remains cash;
- non-authoritative public closes may support the model portfolio only, never real brokerage execution or valuation-grade claims.

## Deliverables

- `control/ETF_EU_CAPITAL_ACTIVATION_POLICY_V1.md`
- `config/etf_eu_target_allocation.yml`
- `runtime/build_etf_eu_allocation_decision.py`
- `tools/validate_etf_eu_allocation_decision.py`
- `runtime/apply_etf_eu_guarded_capital_activation.py`
- `tools/validate_etf_eu_guarded_capital_activation.py`
- `runtime/render_etf_eu_client_grade_v2_funded.py`
- `.github/workflows/run-etf-eu-capital-activation.yml`
- focused tests

## Completion definition

CAP01 is complete only when:

1. a fresh pricing artifact exists;
2. dry-run decision validation passes;
3. only eligible lines are executable;
4. whole-share arithmetic and cash reconcile exactly;
5. explicit guarded model-capital confirmation is present;
6. portfolio state and trade ledger mutate idempotently;
7. valuation history is refreshed;
8. a client-grade v2 report is generated from the funded state;
9. control state records the result.
