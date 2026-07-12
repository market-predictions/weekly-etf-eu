# ETF EU RUN260712 FIX1 — Validator entrypoint fix

Date: 2026-07-12

## Issue

The first PDF repair-preview workflow rendered both language previews, then stopped before machine validation because the workflow executed the validator as a file while that file imported through the `tools` package path.

## Repair

`tools/validate_etf_eu_routine_pdf_client_grade_v2.py` now imports its sibling base validator directly, which is valid for the workflow's direct-file invocation.

Repair commit:

```text
b86b817fc7f4767466de08c5889cde639b59326d
```

Regression test commit:

```text
70ed41297c4340f615ecd439d648918044dae99e
```

## Boundaries

```text
preview_rendering_reached=true
machine_validation_reached=false
correction_delivery_performed=false
receipt_check_performed=false
portfolio_mutation=false
```

## Next action

Start a new `Weekly ETF EU routine PDF repair preview` run from current `main`. Do not rerun the historical failed job.
