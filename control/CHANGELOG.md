# Weekly ETF EU Review OS — Changelog

This file records integration-level changes made to the EU/UCITS ETF review repository.

---

## 2026-06-04 — Consolidate control files after agreement-aware pricing-surface work

Updated control documentation after the source metadata, agreement gate, valuation bridge, pricing-surface wrapper, fundability contract and shadow workflow work moved the repo beyond the M1 adapter-only state.

Files updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/CHANGELOG.md
control/DECISION_LOG.md
```

Marked completed:

- PR `#8` — source metadata policy;
- PR `#9` — agreement gate;
- PR `#10` — valuation agreement bridge;
- pricing-surface report wrapper;
- fundability promotion contract;
- non-production pricing-surface shadow workflow created.

Marked pending:

- shadow workflow verification;
- main workflow wrapper switch;
- production Dutch-first report;
- delivery enablement.

Authority boundaries after consolidation:

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

Important verification note:

The shadow workflow exists, but the latest queue commits did not return connector-visible workflow-run evidence. The shadow workflow must therefore remain `pending verification` until GitHub Actions confirms success or a validation evidence artifact is committed under `output/validation/`.

---

## 2026-06-04 — Add non-production pricing-surface shadow workflow

Commit:

```text
03e7b539b8bc26c746db51c1db383f728e773e71
```

Follow-up queue trigger update:

```text
4b458a30405958b06e833bdb4de73cabf48c6d8c
```

Files changed:

```text
.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml
```

Summary:

- added a non-production workflow for agreement-aware pricing-surface validation;
- workflow runs wrapper tests, pricing candidates, pricing preflight, agreement-aware valuation artifact, report pricing-surface renderer, output validators, pricing-surface validator and fundability validator;
- later made the workflow queue-triggerable from `control/run_queue/weekly_etf_eu_pricing_surface_shadow_request_*.md`;
- later added non-production validation evidence writing under `output/validation/`.

Authority boundaries:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

Verification status:

```text
pending
```

Do not claim the workflow passed until run/job evidence or committed validation evidence exists.

---

## 2026-06-04 — Add UCITS fundability promotion contract

Commits:

```text
46615795029311920f6a3d3a7cf8e91c668a174e
3675b57072093dbad8144931c11b7f114d860c77
```

Files changed:

```text
control/UCITS_FUNDABILITY_PROMOTION_CONTRACT_V1.md
tools/validate_ucits_fundability_promotion_contract.py
tests/test_ucits_fundability_promotion_contract.py
```

Summary:

- defined gates required before a UCITS candidate can move toward `fundable` status;
- separated `verified_candidate_not_funded` from `fundable`;
- blocked automatic promotion from pricing evidence, report visibility or registry presence;
- added tests so bootstrap candidates remain not funded and not fundable.

Authority boundaries:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

---

## 2026-06-04 — Add pricing-surface report wrapper and validator

Representative commits:

```text
9707db1a10b3f402c91fdddd1c91a5cb16576693
ef6c69a4a5ba35a207a7052e780ff07afe9cd164
2327f6d3fa277aca004acd94d8e1378d935cc72b
d68d6311cd0eaa3c5830f4ec4d9cf9fb3e4fcc81
```

Files changed include:

```text
runtime/render_etf_eu_report_with_pricing_surface.py
runtime/etf_eu_pricing_surface.py
tools/validate_etf_eu_pricing_surface.py
tests/test_etf_eu_pricing_surface.py
tests/test_etf_eu_report_pricing_surface_wrapper.py
control/WORKFLOW_WRAPPER_WIRING_DECISION_20260604.md
```

Summary:

- added a report wrapper that can display agreement-gate pricing evidence;
- added Dutch and English pricing-surface validation;
- refined forbidden-phrase checks to block positive valuation/funding authority while allowing explicit negated disclaimers;
- recorded intended safe workflow wiring in a control file.

Authority boundaries:

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

---

## 2026-06-04 — Integrate valuation agreement bridge

Merge commit:

```text
51f91751e8df19bc5879b4a6ee4c3280e663c55e
```

Integrated PR:

```text
#10 — Draft: Add agreement-aware valuation artifact bridge
```

Files changed:

```text
control/VALUATION_AGREEMENT_INTEGRATION_PLAN_20260604.md
pricing/valuation_agreement_evidence.py
pricing/enrich_ucits_valuation_agreement.py
pricing/build_ucits_valuation_prices_with_agreement.py
tests/test_valuation_agreement_evidence.py
tests/test_build_ucits_valuation_prices_with_agreement.py
```

Summary:

- added an agreement-aware wrapper path around the existing valuation artifact builder;
- attached `agreement_gate_evidence` to valuation rows;
- preserved conservative current artifact behavior:
  - `valuation_grade=false`;
  - `valuation_grade_row_count=0`;
  - no pricing-source promotion;
  - no funding authority;
  - no portfolio mutation;
  - no production delivery.

Authority boundaries:

```text
no workflow changes by PR #10 itself
no output artifact changes by PR #10 itself
no portfolio state changes
no report renderer changes
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

---

## 2026-06-04 — Integrate agreement gate

Merge commit:

```text
575f919614690a3a851dc4968dea0cfe3a1a870d
```

Integrated PR:

```text
#9 — M1: Add agreement gate integration
```

Files changed:

```text
pricing/price_agreement_gate.py
tools/validate_price_agreement_gate.py
tests/test_price_agreement_gate.py
```

Summary:

- added deterministic agreement-gate classification:
  - `valuation_grade`;
  - `provisional`;
  - `blocked`;
- used source metadata policy to count only sources with market-close agreement authority;
- kept issuer NAV/reference evidence out of independent market-close agreement counting;
- preserved Yahoo/yfinance as insufficient by itself for valuation authority.

Validation reported in PR:

```text
python -m pytest tests/test_price_agreement_gate.py -q
6 passed in 0.10s

python tools/validate_price_agreement_gate.py
PRICE_AGREEMENT_GATE_OK
```

Authority boundaries:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no workflow changes
no output artifact changes
no report renderer changes
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

---

## 2026-06-04 — Integrate source metadata policy

Merge commit:

```text
270446ee54d7f97223b2b94f6207ec2b7c88de22
```

Integrated PR:

```text
#8 — M5: Add source metadata policy
```

Files changed:

```text
control/DATA_SOURCE_METADATA.md
pricing/source_metadata_policy.py
tests/test_source_metadata_policy.py
```

Summary:

- added explicit metadata categories for pricing sources;
- added deterministic helper policy modes;
- prepared the agreement-gate path without promoting any source evidence to valuation authority.

Validation reported in PR:

```text
python -m pytest tests/test_source_metadata_policy.py -q
9 passed in 0.12s
```

Authority boundaries:

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

---

## 2026-06-04 — Consolidate M1 pricing-spine integration state

Updated control documentation after the M1 pricing-spine worker phase completed.

Files updated:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/CHANGELOG.md
control/DECISION_LOG.md
```

Scope:

- reflected PRs `#3`–`#7` as merged;
- marked common pricing interface and provider-adapter integration as done;
- made source metadata policy the next immediate work item at that time;
- kept agreement gate queued after source metadata policy at that time;
- kept first report pricing surface blocked until agreement-gate output existed at that time;
- recorded stable pricing-spine authority decisions in the decision log.

Authority boundaries after consolidation:

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

---

## 2026-06-03 — Integrate M1 provider-adapter workstreams

Integrated PRs:

```text
#3 — M1: Add common pricing interface — 0c21629aa315f18a0ebceb0a301841d457d2a554
#4 — M1: Add Stooq pricing adapter — c92cff7a973f27f152b4c866515d7c84e28135d6
#5 — M1: Add Börse Frankfurt / Xetra pricing adapter — 34d6c909e87015de49e31ed3fc25294084faad16
#6 — M1: Add Yahoo fallback pricing adapter — 9138efd0d5613527bd6ab6f44313596e6cb6907f
#7 — M1: Add issuer NAV reference adapter — 7b74a36de88b8fdb5b4a4f8709312df533c27a9d
```

Summary:

- added typed `PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult` interface;
- added Stooq, Börse Frankfurt / Xetra, Yahoo/yfinance and issuer NAV adapters;
- kept Stooq provisional/cross-check only;
- kept Börse Frankfurt / Xetra as exchange-candidate evidence pending source/license review;
- kept Yahoo/yfinance fallback/provisional only;
- kept issuer NAV reference/stale-check only.

Authority boundaries:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no candidate promotion to fundable
```

---

## 2026-06-03 — Integrate M0 ground-clearing workstream

Commit:

```text
c1476171606206d369190bf4c8cf126222a1e753
```

Integrated PR:

```text
#1 — M0 ground-clearing: pin dependencies and document EU bootstrap workflow
```

Files changed:

```text
.gitignore
README.md
archive/README.md
requirements.txt
```

Summary:

- added repository README for EU bootstrap orientation;
- added archive/quarantine notes for inherited U.S./intraday and sender artifacts;
- pinned local/bootstrap dependencies;
- added local clutter ignore rules while preserving `control/run_queue` and `output/*` behavior.

Authority boundaries:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```
