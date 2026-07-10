# Decision — ETF-EU-MVP24 Fresh Generation Renderer Integration

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP24_FRESH_GENERATION_RENDERER_INTEGRATION_DECISION_20260710`

## Decision

Close MVP24 as renderer-integrated for the fresh-generation package, while keeping delivery separately gated.

```text
status=completed_fresh_generation_renderer_integrated
upstream_pattern_adapted=weekly-etf renderer/package concept; adapted for EU/UCITS fresh package generation
selected_next_package=ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE
```

## Upstream basis

MVP24 inspected the mature upstream `weekly-etf` renderer/package flow:

```text
runtime/build_etf_report_state.py
runtime/render_etf_report_from_state.py
send_report_runtime_html.py
send_report.py
tools/write_weekly_etf_run_manifest.py
tools/validate_etf_manifest_evidence.py
```

The upstream pattern separates runtime state, markdown rendering, HTML/PDF delivery assets, run manifests, evidence validation and artifact persistence.

## EU adaptation

The EU package builder keeps a thinner EU-specific renderer instead of porting the U.S. renderer directly.

Reason:

```text
U.S. renderer uses U.S. ETF filenames, U.S. portfolio state and U.S. holdings semantics.
EU output must use EU-authoritative state and preserve Dutch-primary / English-companion authority boundaries.
```

New MVP24 path:

```text
control/ETF_EU_FRESH_GENERATION_RENDERER_INTEGRATION_CONTRACT_V1.md
→ tools/build_etf_eu_fresh_generation_package.py
→ output/fresh_generation/weekly_etf_eu_review_nl_260710.md
→ output/fresh_generation/weekly_etf_eu_review_260710.md
→ output/fresh_generation/weekly_etf_eu_review_nl_260710.html
→ output/fresh_generation/weekly_etf_eu_review_260710.html
→ output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
→ output/fresh_generation/weekly_etf_eu_review_260710.pdf
→ output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
→ output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
→ output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

## Authority rules

MVP24 may generate a fresh package only.

It must not create:

```text
send_executed=true
transport_attempted=true
receipt_confirmed=true
valuation_grade=true
funding_authority=true
portfolio_mutation=true
production_delivery_authority=true
```

`ready_for_controlled_delivery=false` remains correct until MVP25 runs a dedicated package-readiness gate.

## Consequence

MVP24 answers the package question as follows:

```text
fresh_full_package_generation_from_eu_state=true
pdf_generation_status=generated
ready_for_controlled_delivery=false
```

The next package should be:

```text
ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE
```
