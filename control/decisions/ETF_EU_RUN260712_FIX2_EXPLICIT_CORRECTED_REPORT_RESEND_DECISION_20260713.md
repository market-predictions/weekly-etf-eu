# ETF EU RUN260712 FIX2 — Correction package decision

Date: 2026-07-13

## Scope

Create an immutable correction package for the Weekly ETF EU report dated 2026-07-12. The package uses only the four approved files under `output/repair_preview/20260712_200000/`.

## Donor pattern

Inspected in `market-predictions/weekly-etf`:

```text
.github/workflows/send-weekly-report.yml
tools/write_etf_delivery_manifest_summary.py
tools/write_weekly_etf_run_manifest.py
tools/validate_etf_manifest_evidence.py
```

Adapted:

```text
explicit report paths
rendered-output validation
redacted recipient evidence
transport and receipt separation
run-manifest closeout
```

Not adopted as EU authority:

```text
U.S. portfolio state
U.S. holdings
U.S. recipients
U.S. report discovery
U.S. recommendation logic
```

## Stable decisions

- The existing EU transport module is extended; a second transport implementation is not created.
- The original analysis and portfolio decision remain unchanged.
- The original malformed PDFs are excluded from the correction package.
- Source and delivery SHA-256 values must match.
- The original transport evidence remains immutable.
- Correction artifacts use separate filenames.
- Recipient and secret values remain redacted or absent.
- Transport success does not establish inbox receipt.
- Independent delayed receipt verification remains mandatory.

## Current state

```text
implementation_ready=true
package_materialization_pending=true
live_execution_selected=false
transport_attempted=false
corrected_resend_executed=false
receipt_confirmed=false
next_action=RUN_CORRECTED_RESEND_VALIDATE_ONLY
```
