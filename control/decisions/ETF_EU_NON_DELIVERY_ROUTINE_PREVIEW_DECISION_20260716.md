# ETF EU Non-Delivery Routine Preview Decision

Date: 2026-07-16
Repository: `market-predictions/weekly-etf-eu`
Status: accepted and implemented

## Current issue

The established routine production workflow couples report generation, validation and guarded delivery. The current authority permits generation and complete visual review but does not authorize transport.

## Root cause

The operational runbook distinguishes report readiness from delivery authority, but the executable routine workflow had only a send-confirmed path. Using that workflow for a preview would either require false send authority or fail after valid report generation.

## Decision framework

Add a separate non-delivery routine preview lane. It may create current pricing evidence, refresh normalized state, generate Dutch and English outputs, run strict machine validation and render all PDF pages for review.

It may not prepare or execute transport.

## Input/state contract

The preview lane uses:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
config/ucits_symbol_registry.yml
current run-scoped pricing evidence
current donor macro evidence adapted for EU use
```

## Output contract

The lane produces four client files, normalized report state, machine gates, rendered review pages and a run-scoped preview manifest.

The preview manifest must state:

```text
production_delivery_authority=false
transport_attempted=false
send_executed=false
receipt_confirmed=false
visual_review_pending=true
```

until complete page review is recorded.

## Operational runbook

```text
new preview request
→ fresh pricing
→ macro and valuation refresh
→ funded-aware report build
→ strict machine validation
→ render every PDF page
→ persist non-delivery preview evidence
→ complete visual review
→ readiness closeout
```

A separate explicit delivery instruction remains required before the existing guarded send path may be used.

## Implementation

```text
.github/workflows/run-weekly-etf-eu-routine-preview.yml
control/run_queue/etf_eu_routine_preview_request_20260716_214500.md
output/run_manifests/etf_eu_routine_preview_queue_manifest_20260716_214500.json
```

## Current execution status

The queue was committed, but no verifiable GitHub Actions run or generated artifact commit appeared from the connector-authored push. The status therefore remains `queued_not_executed`; no generation, rendering, visual-review or delivery success is claimed.
