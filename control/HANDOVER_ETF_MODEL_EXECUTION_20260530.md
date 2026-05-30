# Handover — Weekly ETF Model Execution / Portfolio Rotation

**Repo:** `market-predictions/weekly-etf`  
**Date:** 2026-05-30  
**Status:** active debug / development handover  
**Primary topic:** converting ETF rotation from recommendation-only into self-steering model-portfolio execution.

---

## 1. Start here in a fresh chat

Read the repo control layer first, in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. this file: `control/HANDOVER_ETF_MODEL_EXECUTION_20260530.md`
5. then inspect only the minimum relevant execution files listed below.

Do **not** assume ChatGPT state is the source of truth. GitHub is the source of truth.

---

## 2. Current issue

The weekly ETF portfolio rotation engine now produces valid rotation intent, especially the generic GLD → GSG rotation, but the model-execution layer has been unstable while moving from report-only recommendations to actual persisted model-portfolio changes.

Recent problem pattern:

```text
Build runtime ETF state and reports
→ shadow execution artifact created
→ validate_etf_model_execution.py fails
→ nav_drift_too_large: 5501.66
```

The failing run showed:

```text
ETF_MODEL_EXECUTION_OK | artifact=output/runtime/etf_model_execution_20260529_20260530_121614.json | mode=shadow | trades=1 | status=shadow_ready
RuntimeError: ETF model execution validation failed ... nav_drift_too_large:5501.66
```

---

## 3. Root cause found so far

This is not primarily a pricing issue and not only a notional-cap issue.

The deeper cause is an **authority conflict** between:

### Official executed state

`output/etf_portfolio_state.json` already showed GLD partially sold and GSG added:

```text
GLD shares: 13.6192
GLD market_value_eur: 4871.53
GSG shares: 201.749658
GSG market_value_eur: 5501.65
```

### Runtime state used for execution

The runtime report state still showed stale GLD share count in some execution-facing fields:

```text
GLD shares: 29
GLD market_value_eur: 4871.53
GSG already present around 5% NAV
```

This contradictory state likely came from stale recommendation-scorecard memory:

```text
output/etf_recommendation_scorecard.csv
```

That scorecard still had the older GLD line from 2026-05-05:

```text
GLD shares: 29
GLD market_value_eur: 10495.36
```

In plain terms:

```text
scorecard memory was allowed to overwrite execution-critical fields
```

That made the model-execution engine think there were still 29 GLD shares available while the portfolio state had already partly rotated. The result was an artificial NAV drift when the engine simulated or validated another GLD → GSG pass.

---

## 4. Latest fix applied before this handover

Updated:

```text
runtime/model_execution_engine.py
```

Latest relevant commit:

```text
807d32141186cf9156aae0c220e380914db4df88
```

Intent of the fix:

```text
Use output/etf_portfolio_state.json as the execution authority.
Do not let runtime/report/scorecard-enriched position rows override official shares or official market values.
```

Added logic:

```text
_prepare_runtime_state(...)
```

This function overlays official portfolio-state positions before shadow/guarded model execution. It should ensure execution sees official state for:

```text
shares
current_price_local
previous_price_local
currency
market_value_local
market_value_eur
current_weight_pct
previous_weight_pct
target_weight_pct
```

Also updated logic so execution notional is based on official available source value, not stale scorecard share count.

---

## 5. Latest run queued before this handover

Created:

```text
control/run_queue/weekly_etf_report_request_20260530_124000.md
```

Commit:

```text
e8a6766ca2a4a6a01b576e51ff0ceded6acf2d60
```

Purpose:

```text
Test whether model execution now uses official portfolio state instead of stale scorecard-enriched runtime state.
```

This queued run has **not been confirmed successful in this chat**. In the next chat, first inspect the latest GitHub Actions run after commit `e8a6766ca2a4a6a01b576e51ff0ceded6acf2d60`.

---

## 6. Key files to inspect next

### Control / design authority

```text
control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md
control/ETF_PORTFOLIO_ROTATION_ROADMAP.md
control/ETF_PORTFOLIO_ROTATION_CHANGELOG.md
control/HANDOVER_ETF_MODEL_EXECUTION_20260530.md
```

### Workflow

```text
.github/workflows/send-weekly-report.yml
```

Important workflow path:

```text
pricing
→ lane discovery
→ portfolio_rotation_engine
→ build_etf_report_state
→ render reports
→ shadow model_execution_engine
→ validate_etf_model_execution
→ content/pricing/render validators
→ persist valuation state
→ guarded_auto model_execution_engine
→ validate_etf_model_execution with report finalization
→ HTML/PDF render
→ send email
→ commit artifacts
```

### Execution files

```text
runtime/portfolio_rotation_engine.py
runtime/model_execution_engine.py
tools/validate_etf_model_execution.py
runtime/finalize_executed_etf_report.py
runtime/build_etf_report_state.py
```

### State / output files

```text
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/runtime/latest_etf_model_execution_path.txt
output/runtime/etf_model_execution_*.json
output/runtime/etf_report_state_*.json
output/runtime/etf_rotation_plan_*.json
```

---

## 7. Decision framework

The self-steering model must follow these authority rules:

### A. Rotation decision authority

The rotation engine may use:

```text
scorecard
lane discovery
relative strength
pricing audit
portfolio context
```

This is allowed because the rotation engine is deciding what should happen.

### B. Execution quantity authority

The model-execution engine must use only:

```text
output/etf_portfolio_state.json
current pricing audit
cash balance
trade_intents from the current rotation plan
```

It must **not** use stale scorecard fields for execution-critical quantities.

### C. Report authority after execution

The final delivered report must be rebuilt from:

```text
executed output/etf_portfolio_state.json
```

not from the pre-execution runtime state.

### D. Broker boundary

Everything here is **model-portfolio execution only**. It does not place broker orders.

---

## 8. Input / state contract

For execution, the authoritative inputs are:

```text
output/etf_portfolio_state.json
output/pricing/price_audit_*.json
output/runtime/etf_rotation_plan_*.json
```

The following should be treated as advisory/contextual, not execution quantity authority:

```text
output/etf_recommendation_scorecard.csv
rendered report markdown
runtime state after scorecard enrichment
```

Execution-critical fields that must not be overwritten by stale memory:

```text
shares
currency
current_price_local
previous_price_local
market_value_local
market_value_eur
current_weight_pct
previous_weight_pct
cash_eur
nav_eur
```

---

## 9. Output contract

A successful self-steering model run should produce:

```text
output/runtime/etf_model_execution_<date>_<run_id>.json
output/etf_trade_ledger.csv updated with official model Sell/Buy rows
output/etf_portfolio_state.json updated with post-trade holdings
output/runtime/etf_report_state_<date>_<run_id>_executed.json
final EN/NL markdown reports rebuilt from executed holdings
final delivery HTML/PDF generated from executed reports
```

Expected visible result if GLD → GSG remains selected by generic rules:

```text
Section 14: executed model changes, not only proposed trade intents
Section 15: reduced GLD and existing/new GSG reconcile with state
Final report should not say GLD → GSG is still pending after guarded execution has persisted it
```

---

## 10. Operational runbook for next chat

### Step 1 — Check the latest Actions run

Inspect the run triggered by:

```text
control/run_queue/weekly_etf_report_request_20260530_124000.md
```

Focus on step:

```text
Build runtime ETF state and reports
```

If it still fails with:

```text
nav_drift_too_large: 5501.66
```

then the execution engine still does not fully isolate execution state from stale scorecard/runtime fields.

### Step 2 — Inspect latest model execution artifact

Open:

```text
output/runtime/latest_etf_model_execution_path.txt
```

Then inspect the referenced JSON.

Check:

```text
pre_trade_portfolio.total_portfolio_value_eur
post_trade_shadow_portfolio.nav_drift_eur
proposed_ledger_rows[].estimated_notional_eur
shadow_positions for GLD and GSG
```

Expected:

```text
nav_drift_eur close to 0
GLD source sell equals GSG destination buy
no stale 29-share GLD if official state says 13.6192 shares
```

### Step 3 — If stale GLD still appears

Search in `runtime/model_execution_engine.py` for any path that still consumes `runtime_state["positions"]` before `_prepare_runtime_state()` is applied.

Possible follow-up patches:

1. Move official-state overlay even earlier.
2. Add a hard validator comparing execution source position fields against `output/etf_portfolio_state.json` before allowing execution.
3. Block if runtime execution shares differ from official state shares by more than a tiny tolerance.
4. Add a regression validator specifically for stale scorecard override.

### Step 4 — After execution succeeds

Verify:

```text
output/etf_trade_ledger.csv
output/etf_portfolio_state.json
output/runtime/etf_report_state_*_executed.json
latest EN/NL PDFs
```

Do not claim report delivery succeeded unless the Send email step completed and a real delivery artifact/manifest exists.

---

## 11. Known design risk

The current pipeline still has a fragile interaction:

```text
build_etf_report_state.py enriches portfolio rows with scorecard fields
```

That is acceptable for investor-facing context, but dangerous for execution if not isolated.

Best long-term solution:

```text
Separate portfolio execution state from report enrichment state.
```

Recommended durable architecture:

```text
ExecutionState = portfolio_state + fresh prices + trade_intents
ReportState = ExecutionState + scorecard + macro + lane narratives
```

Do not let ReportState feed back into ExecutionState for quantities.

---

## 12. Current recommended next development task

Add a dedicated validator:

```text
tools/validate_etf_execution_state_authority.py
```

It should fail if execution input has any mismatch versus official portfolio state for:

```text
ticker
shares
market_value_eur
currency
cash_eur
```

Suggested checks:

```text
For every official holding:
- ticker exists in execution state
- shares match official state after current pricing overlay
- market value reconciles to shares × selected close / FX
- no scorecard value overrides official shares
- no destination buy can occur without equal source sell or cash debit
```

This validator should run before both shadow and guarded execution.

---

## 13. Stable decisions to keep

1. No ticker-specific hard rules. GLD → GSG must be produced by generic rotation logic, not a GLD exception.
2. The portfolio should become self-steering; no weekly human approval loop.
3. Guarded auto-execution is acceptable only when hard validators pass.
4. Execution means model-portfolio state mutation, not real broker trading.
5. Report must reflect executed model state if execution has already been persisted.
6. Stale report/scorecard memory may inform decision quality but must never override execution quantities.

---

## 14. Suggested updates after the next run

If the latest run succeeds:

- Update `control/CURRENT_STATE.md` with: guarded auto model execution now uses official portfolio-state authority and latest run passed.
- Update `control/NEXT_ACTIONS.md` with: add regression validator for execution-state authority and stale scorecard override.
- Update `control/DECISION_LOG.md` with: official portfolio state is the sole authority for model-execution quantities.

If the latest run fails:

- Update `control/CURRENT_STATE.md` with the exact failing step and artifact path.
- Keep `control/NEXT_ACTIONS.md` focused on separating `ExecutionState` from `ReportState`.
