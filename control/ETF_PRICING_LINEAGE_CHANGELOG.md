# ETF Pricing Lineage Changelog

This file is the central changelog for the ETF pricing-lineage repair track. It is separate from the root `changelog.md` so pricing regressions, design decisions, and validation changes can be reviewed without scanning unrelated rendering, localization, or delivery changes.

## Rules

- Record every meaningful pricing-lineage design, code, workflow, validation, and state-contract change.
- Keep entries implementation-facing and regression-friendly.
- Include why the change was made, what changed, affected files, and validation evidence.
- Do not use this file for ordinary report content changes unless they affect pricing lineage.
- Keep root `changelog.md` updated for repo-level visibility; keep this file as the detailed pricing-lineage log.

---

## 2026-05-24 — Create ETF Pricing Lineage Contract V1

### Current issue

The ETF report can now display a per-holding close-price disclosure table that reconciles internally with Section 7 and Section 15, but the repository still lacks a hard proof that one immutable pricing audit flows through runtime state, English/Dutch report render, persisted portfolio state, valuation history, and delivery manifest.

### Root cause

The existing system still relies too heavily on latest-file selection and report-time runtime derivation. It can show fresh prices without also proving immutable audit identity, provider symbol lineage, exact close-date semantics, independent verification, and post-run state persistence.

### What changed

- Added `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`.
- Defined the target artifact chain:
  - requested close date and report token
  - immutable pricing audit
  - explicit run manifest
  - runtime report state
  - English/Dutch reports
  - delivery assets
  - persisted portfolio state
  - persisted valuation history
- Defined the required status split:
  - `fresh_exact_close`
  - `fresh_exact_unverified`
  - `prior_valid_close`
  - `carried_forward`
  - `unresolved`
  - `blocked`
- Defined valuation-grade versus research-grade challenger pricing tiers.
- Defined the required future hard validator: `tools/validate_etf_pricing_lineage_contract.py`.

### Weekly Index lesson imported

The Weekly Index repo already has a stronger pattern where pricing writes canonical state and valuation history, and the workflow commits pricing, runtime, report, manifest, state, and candidate artifacts back to the repo. ETF should copy that operating discipline.

### Improvement beyond Weekly Index

ETF should not copy Weekly Index blindly. The ETF contract requires stronger immutable run identity, exact/prior close-date semantics, provider-symbol lineage, independent verification, and valuation-grade challenger enforcement.

### Affected files

- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`

### Validation / evidence

No runtime code was changed in this entry. This is a design/control-layer commit that defines the implementation target before touching production pricing code.

---

## Open regression themes to close

### A. Latest-file ambiguity

Current ETF runtime components can still select the latest audit or latest runtime state independently. Future implementation must pass explicit audit and manifest paths through the workflow.

### B. State persistence gap

Current ETF reports can derive a new runtime NAV without updating `output/etf_portfolio_state.json` and `output/etf_valuation_history.csv` as canonical state.

### C. Weak fresh-close semantics

A provider row on or before the requested date must not be labeled generically as fresh. The status must distinguish exact requested close from prior valid market close.

### D. Challenger pricing tier ambiguity

Broad discovery can remain research-grade. Replacement-duel challengers and promoted fundable candidates require valuation-grade pricing before being presented as actionable.

### E. Missing independent verification

Provider closes should be cross-checked where feasible. When cross-check is unavailable, the audit must say so explicitly.
