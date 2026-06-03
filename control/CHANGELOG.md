# Weekly ETF EU Review OS — Changelog

This file records integration-level changes made to the EU/UCITS ETF review repository.

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
