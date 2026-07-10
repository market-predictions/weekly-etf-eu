# Decision — ETF EU Upstream-First Reuse Rule

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710`

## Decision

For every new ETF EU task, work package, workflow change, runtime script, validator, renderer, delivery step, or control file, first inspect the upstream `market-predictions/weekly-etf` repository before designing or implementing the EU change.

The default implementation posture is:

```text
check upstream weekly-etf
→ identify mature concept/file/contract
→ borrow or adapt the proven pattern
→ diverge only with explicit EU authority reason
```

## Rationale

The upstream `weekly-etf` repo already contains mature implementation layers for runtime report generation, bilingual delivery, HTML/PDF rendering, pre-send validation, SMTP dispatch, redacted delivery manifest summaries, final run manifests, and artifact persistence.

The EU repo should not recreate those mechanisms blindly. It should reuse the upstream architecture where the concept is applicable, while preserving UCITS/EU authority boundaries.

## Current delivery comparison finding

The upstream `weekly-etf` workflow uses this pattern:

```text
runtime/pricing/report generation
→ pre-send report and delivery validators
→ send_report_runtime_html.py
→ send_report.py / send_report_OLD.py SMTP send
→ tools/write_etf_delivery_manifest_summary.py
→ tools/write_weekly_etf_run_manifest.py
→ commit run artifacts
```

For `weekly-etf-eu`, the correct adaptation is not a blind copy because the upstream sender still relies on `weekly_analysis*` report discovery and legacy recipient assumptions. The EU path should borrow the delivery evidence and redaction pattern, while using explicit EU package-bound inputs.

## Stable authority rule

Borrow from upstream:

```text
rendering concepts
delivery asset concepts
SMTP send discipline
redacted recipient evidence
delivery manifest summaries
run manifest closeout patterns
pre-send validation gates
artifact persistence discipline
```

Do not borrow as authority:

```text
U.S. ETF holdings
U.S. portfolio state
U.S. investment universe
U.S. report filenames as EU identity
U.S. recipient authority
U.S. delivery authority
U.S. valuation or funding assumptions
```

## Required behavior for future work

Every future worker should record one of these outcomes before creating or materially changing a file:

```text
upstream_pattern_reused=<file or concept>
upstream_pattern_adapted=<file or concept + reason>
upstream_pattern_rejected=<file or concept + EU authority reason>
no_upstream_equivalent_found=<search terms / inspected files>
```

## Consequence

`control/SYSTEM_INDEX.md` now includes an upstream-first reuse rule. Future ETF EU work must inspect `market-predictions/weekly-etf` before implementing new EU machinery, especially around workflows, runtime, validators, rendering, delivery evidence, run manifests, and closeout artifacts.
