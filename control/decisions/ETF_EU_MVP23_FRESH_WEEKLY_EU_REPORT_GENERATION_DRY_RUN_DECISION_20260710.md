# Decision — ETF-EU-MVP23 Fresh Weekly EU Report Generation Dry Run

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN_DECISION_20260710`

## Decision

Close MVP23 as a no-send fresh-generation dry-run scaffold.

```text
status=completed_fresh_generation_dry_run_scaffold
upstream_pattern_adapted=weekly-etf fresh-generation/runtime/report-manifest concept; adapted for EU dry-run and UCITS authority boundaries
selected_next_package=ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
```

## Upstream basis

MVP23 inspected the mature upstream `weekly-etf` fresh-generation/runtime flow:

```text
.github/workflows/send-weekly-report.yml
pricing/run_pricing_pass.py
runtime/build_etf_report_state.py
runtime/render_etf_report_from_state.py
tools/write_weekly_etf_run_manifest.py
tools/validate_etf_manifest_evidence.py
```

The upstream pattern resolves run identity, pricing, runtime state, report rendering, run-manifest writing, validation, and delivery evidence.

## EU adaptation

The EU repo does not yet have a fully integrated fresh-generation renderer equivalent to upstream that can produce a complete fresh Dutch-primary / English-companion PDF package from EU state.

MVP23 therefore creates a deterministic scaffold:

```text
control/ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1.md
→ tools/build_etf_eu_fresh_generation_dry_run.py
→ output/fresh_generation/*_dry_run.md
→ output/fresh_generation/*_dry_run.html
→ output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
→ output/fresh_generation/etf_eu_ready_for_controlled_delivery_dry_run_20260710_000000.json
→ tools/validate_etf_eu_fresh_generation_dry_run.py
→ output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
```

## Authority rules

MVP23 may prove a no-send generation scaffold only.

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

Generation and delivery remain separate. A future package must integrate the actual EU renderer/package builder before any fresh package can be considered ready for controlled delivery.

## Consequence

MVP23 answers the key question as follows:

```text
fresh_full_package_generation_from_eu_state=false
fresh_generation_scaffold_from_eu_state=true
ready_for_controlled_delivery=false
```

The next package should be:

```text
ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
```
