# Weekly ETF EU Review OS — Changelog

This file records integration-level changes made to the EU/UCITS ETF review repository.

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
- made source metadata policy the next immediate work item;
- kept agreement gate queued after source metadata policy;
- kept first report pricing surface blocked until agreement-gate output exists;
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

No pricing execution code, workflow, output file, portfolio state, report renderer, PDF/email or delivery behavior was changed.

---

## 2026-06-03 — Integrate M1 issuer NAV reference adapter

Commit: `7b74a36de88b8fdb5b4a4f8709312df533c27a9d`

Integrated PR:

```text
#7 — M1: Add issuer NAV reference adapter
```

Files changed:

```text
pricing/sources/issuer_nav.py
tests/test_issuer_nav_adapter.py
tests/fixtures/pricing/issuer_nav/valid_cspx_nav.json
tests/fixtures/pricing/issuer_nav/missing_currency_nav.json
```

Summary:

- added issuer NAV/reference adapter using the shared pricing interface;
- implemented `PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult`;
- kept issuer NAV as reference/stale-check evidence only;
- confirmed issuer NAV is not exchange EOD close authority and does not count as independent market-close agreement evidence.

Validation reported in PR:

```text
python -m pytest tests/test_issuer_nav_adapter.py -q
4 passed in 0.19s
```

Authority boundaries after merge:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```

---

## 2026-06-03 — Integrate M1 Yahoo fallback pricing adapter

Commit: `9138efd0d5613527bd6ab6f44313596e6cb6907f`

Integrated PR:

```text
#6 — M1: Add Yahoo fallback pricing adapter
```

Files changed:

```text
pricing/sources/yahoo.py
tests/test_yahoo_adapter.py
tests/fixtures/pricing/yahoo/cspx_history.json
tests/fixtures/pricing/yahoo/empty_history.json
tests/fixtures/pricing/yahoo/missing_close_history.json
```

Summary:

- added Yahoo/yfinance adapter using the shared pricing interface;
- implemented `PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult`;
- kept Yahoo as fallback/provisional evidence only;
- confirmed Yahoo does not create valuation-grade rows or mutate portfolio state.

Validation reported in PR:

```text
python -m pytest tests/test_yahoo_adapter.py -q
8 passed in 0.17s
```

Authority boundaries after merge:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```

---

## 2026-06-03 — Integrate M1 Börse Frankfurt / Xetra pricing adapter

Commit: `34d6c909e87015de49e31ed3fc25294084faad16`

Integrated PR:

```text
#5 — M1: Add Börse Frankfurt / Xetra pricing adapter
```

Files changed:

```text
config/source_symbol_overrides/boerse_frankfurt.yml
pricing/sources/boerse_frankfurt.py
tests/fixtures/pricing/boerse_frankfurt/currency_uncertain.json
tests/fixtures/pricing/boerse_frankfurt/no_close.json
tests/fixtures/pricing/boerse_frankfurt/resolved_close.json
tests/test_boerse_frankfurt_adapter.py
```

Summary:

- added Börse Frankfurt / Xetra adapter using the shared pricing interface;
- implemented `PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult`;
- kept the endpoint as undocumented/free pending source/license review;
- kept the adapter as exchange-candidate evidence only, not valuation authority.

Validation reported in PR:

```text
python -m pytest tests/test_boerse_frankfurt_adapter.py -q
4 passed
```

Authority boundaries after merge:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```

---

## 2026-06-03 — Integrate M1 Stooq pricing adapter

Commit: `c92cff7a973f27f152b4c866515d7c84e28135d6`

Integrated PR:

```text
#4 — M1: Add Stooq pricing adapter
```

Files changed:

```text
pricing/sources/stooq.py
config/source_symbol_overrides/stooq.yml
tests/test_stooq_adapter.py
tests/fixtures/pricing/stooq/cspx_daily.csv
tests/fixtures/pricing/stooq/no_data.csv
```

Summary:

- added Stooq adapter using the shared pricing interface;
- implemented `PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult`;
- kept Stooq provisional / cross-check only;
- retained explicit-only source-symbol mappings.

Validation reported in PR:

```text
PYTHONPATH=. pytest tests/test_stooq_adapter.py -q
3 passed
```

Authority boundaries after merge:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```

---

## 2026-06-03 — Integrate M1 common pricing interface

Commit: `0c21629aa315f18a0ebceb0a301841d457d2a554`

Integrated PR:

```text
#3 — M1: Add common pricing interface
```

Files changed:

```text
pricing/README.md
pricing/price_result_schema.py
pricing/source_selection.py
pricing/sources/__init__.py
pricing/sources/base.py
tests/fixtures/pricing/fake_price_rows.json
tests/test_pricing_interface.py
```

Summary:

- added typed pricing spine only;
- introduced `PriceIdentity`, `SourceLineage`, `PriceResult`, `PriceRequest`, abstract `PriceSource`, shared status constants, license constants and authority-tier constants;
- added config-driven source selection helper;
- documented adapter implementation guidance in `pricing/README.md`.

Validation reported in PR:

```text
python -m pytest tests/test_pricing_interface.py -q
5 passed
```

Authority boundaries after merge:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no valuation-grade promotion
```

---

## 2026-06-03 — Coordinator review of Börse Frankfurt / Xetra adapter draft

Reviewed draft PR:

```text
#2 — M1: Add Boerse Frankfurt / Xetra pricing adapter draft
```

Branch:

```text
workstream/boerse-frankfurt-adapter
```

Status:

```text
reviewed_as_draft_not_integrated
```

Coordinator verdict:

- useful adapter draft;
- do not merge before the common pricing interface lands;
- keep as draft handback against the expected interface;
- reconcile local compatibility `PriceQuery` and `PriceResult` with the final shared `pricing/price_result_schema.py` and `pricing/sources/base.py` once available;
- rebase/update branch after the pricing-interface workstream and current `main` settle;
- keep adapter non-authoritative until source policy and agreement gate explicitly classify source evidence.

Files observed in PR scope:

```text
config/source_symbol_overrides/boerse_frankfurt.yml
pricing/sources/__init__.py
pricing/sources/boerse_frankfurt.py
tests/fixtures/pricing/boerse_frankfurt/currency_uncertain.json
tests/fixtures/pricing/boerse_frankfurt/missing_close.json
tests/fixtures/pricing/boerse_frankfurt/resolved_close.json
tests/test_boerse_frankfurt_adapter.py
```

Authority-boundary review:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
valuation_grade_by_adapter=false
```

Integration blockers before merge:

1. Common pricing interface is not merged yet.
2. PR defines local compatibility dataclasses instead of importing final shared `PriceQuery` / `PriceResult` equivalents.
3. `pricing/sources/__init__.py` overlaps with the pricing-interface workstream and must be reconciled after interface integration.
4. The branch is behind current `main` and should be updated before final integration review.
5. The undocumented endpoint assumption must remain explicitly pending license/source review; the adapter must degrade to typed unresolved results on provider drift.
6. Before valuation use, the common interface/agreement gate should distinguish provider-observed close-like records from independently validated completed-session close authority.

No integration merge was performed.

---

## 2026-06-03 — Integrate M0 ground-clearing workstream

Commit: `c1476171606206d369190bf4c8cf126222a1e753`

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

- added a concise repository README that identifies the EU bootstrap workflow and authority boundaries;
- added archive/quarantine notes for inherited U.S./intraday and sender artifacts;
- pinned local/bootstrap dependencies, including `PyYAML` and `yfinance`;
- added local clutter ignore rules while preserving `control/run_queue` and `output/*` behavior.

Coordinator review:

- PR touched only M0-owned files;
- no pricing adapter, valuation builder, validator, workflow, output artifact or control-state file was changed by the PR;
- no GitHub Actions run was attached to the PR head, so integration was based on static diff and authority-boundary review.

Authority boundaries after merge:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```

Deferred follow-up:

- move `prediction.py` into `archive/legacy_us_intraday/` only after active pricing-spine branches settle and imports are rechecked;
- archive duplicate sender variants later while preserving whatever disabled sender marker/facade validators still require.
