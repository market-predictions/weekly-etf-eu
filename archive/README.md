# Archive and quarantine notes

This directory documents inactive inherited material from the original U.S. ETF clone.

## Policy

Archive/quarantine actions must be non-destructive unless the coordinator explicitly approves removal. Historical files may be useful for provenance, regression, or migration reference, but they are not active EU authority unless an EU workflow imports them.

## Current M0 audit — 2026-06-03

### `prediction.py`

Status: inherited intraday / ICT-style calibration script; quarantine candidate.

Audit result:

- the active EU bootstrap workflow `.github/workflows/send-weekly-etf-eu-report.yml` does not call `prediction.py`;
- repository code search found no active `import prediction` / `from prediction` usage;
- the file contains Colab/Google Drive and FX/backtest calibration logic, not current EU UCITS report authority;
- no file move was performed in this branch because moving a large historical file should be coordinated after the parallel pricing-spine workstreams settle.

Recommended coordinator action after merge window:

```text
move prediction.py -> archive/legacy_us_intraday/prediction.py
```

Only do this after confirming no active branch has reintroduced an import or workflow call.

### Sender variants

Status: inherited U.S. sender lineage; quarantine candidate, but keep one active disabled sender facade until the EU delivery layer exists.

Audit result:

- `.github/workflows/send-weekly-report.yml` is disabled and contains the expected `DISABLED_INHERITED_US_ETF_SEND_WORKFLOW` marker;
- the active EU bootstrap workflow validates that the inherited sender workflow remains disabled;
- no sender file was moved in this branch to avoid interfering with validators that inspect the disabled workflow state.

Recommended coordinator action later:

```text
move duplicate sender backups -> archive/legacy_senders/
keep only the minimal disabled sender marker/facade required by validators
```

## Authority reminder

Archive documentation does not grant pricing authority, funding authority, portfolio mutation, PDF rendering, or email delivery authority.
