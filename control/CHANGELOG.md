# Weekly ETF EU Review OS — Changelog

This file records integration-level changes made to the EU/UCITS ETF review repository.

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
