# ETF Portfolio Rotation Engine — Changelog

**Repository:** `market-predictions/weekly-etf`  
**Authority:** `control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md`

---

## 2026-05-28 — Contract, roadmap and skeleton start

Created central build authority and roadmap:

- `control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md`
- `control/ETF_PORTFOLIO_ROTATION_ROADMAP.md`

Created initial implementation skeleton:

- `runtime/portfolio_rotation_engine.py`
- `tools/validate_etf_rotation_output_contract.py`
- `tools/validate_etf_rotation_discipline.py`

Design decisions:

- no ticker-specific rotation rules;
- every incumbent position must re-earn capital generically;
- rotation plan becomes a machine-readable artifact under `output/runtime/`;
- `trade_intents[]` will become the canonical upstream source for trade-ledger writes;
- validators start warning/non-blocking before becoming delivery gates.

---

## 2026-05-28 — Runtime-state integration start

Planned next change:

- `runtime/build_etf_report_state.py` accepts optional `--rotation-plan`;
- runtime state includes `rotation_plan`, `target_weights`, `trade_intents`, and `rotation_decisions` when supplied;
- absence of a rotation plan is warning/non-blocking during v1 buildout.

---

## 2026-05-29 — Client-facing rotation wording cleanup started

Implemented first cleanup in `runtime/rotation_render_tables.py`:

- translated internal reason codes to investor-facing language;
- renamed `Reason codes` / `Redencodes` to rationale/toelichting fields;
- translated override reasons away from raw internal labels;
- kept signed deltas in numeric table columns while moving prose toward client-facing wording.

Remaining cleanup before final validation run:

- delivery HTML prose still needs the same client-facing wording map;
- Dutch quality validator should block raw rotation reason codes and override codes;
- then run a fresh PDF validation pass.
