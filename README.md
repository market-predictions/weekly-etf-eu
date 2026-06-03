# Weekly ETF EU Review OS

This repository is the European / Dutch-client UCITS ETF review workbench derived from `market-predictions/weekly-etf`.

It is **not** a mechanical translation of the U.S. ETF model. U.S.-listed ETFs and inherited U.S. production artifacts are historical scaffolding unless a current EU control file explicitly grants authority.

## Canonical start sequence

For meaningful architecture, pricing, workflow, report or delivery work, read these live GitHub files first:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. the minimum relevant execution files

## Canonical EU bootstrap workflow

The active EU validation entry point is:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

It currently performs EU/UCITS bootstrap validation only. It may build diagnostic pricing artifacts and candidate report skeletons, but it must preserve:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
```

The inherited U.S. send workflow is intentionally disabled:

```text
.github/workflows/send-weekly-report.yml
```

## Current active state authority

Preferred EU state and output paths are documented in `control/SYSTEM_INDEX.md` and `control/CURRENT_STATE.md`.

Current active EU state is cash-only until UCITS investability, valuation pricing, promotion and output contracts are explicitly passed. Historical `output/` files from the cloned U.S. repository are not current EU portfolio truth.

## Inherited artifacts

The repository still contains inherited U.S./intraday/ICT files from the clone. They should be treated as archived provenance or migration raw material unless the active EU workflow imports them.

For M0 ground-clearing, the immediate non-destructive rule is:

- do not delete useful history;
- do not move files that an active workflow imports;
- do not reactivate sender/PDF/email paths;
- document quarantine status before destructive cleanup.

## Dependency discipline

Use `requirements.txt` for local/static validation. The GitHub workflow may still install its minimal dependencies directly until the coordinator updates workflow installation policy.
