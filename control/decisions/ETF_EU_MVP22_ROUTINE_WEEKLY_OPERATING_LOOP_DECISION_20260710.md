# Decision — ETF-EU-MVP22 Routine Weekly Operating Loop

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP22_ROUTINE_WEEKLY_OPERATING_LOOP_DECISION_20260710`

## Decision

Define the repeatable Weekly ETF EU operating loop and manifest contract without yet merging fresh generation and guarded delivery into one production workflow.

```text
status=completed_routine_weekly_operating_loop_defined
upstream_pattern_adapted=weekly-etf routine workflow and run-manifest pattern; adapted for EU/UCITS authority boundaries
fresh_generation_and_guarded_delivery_kept_separate=true
selected_next_package=ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN
```

## Upstream basis

MVP22 inspected the mature upstream `weekly-etf` flow:

```text
.github/workflows/send-weekly-report.yml
tools/write_weekly_etf_run_manifest.py
tools/validate_etf_manifest_evidence.py
runtime/build_etf_report_state.py
runtime/render_etf_report_from_state.py
pricing/run_pricing_pass.py
runtime/discover_etf_lanes.py
runtime/portfolio_rotation_engine.py
```

The upstream pattern resolves a run id/close date, runs pricing, builds discovery and rotation artifacts, builds runtime report state, renders English/Dutch reports, writes run manifests, sends only after validation, writes delivery evidence and commits artifacts.

## EU adaptation

The EU loop borrows:

```text
run identity discipline
pricing → artifact → runtime-state flow
report render path separation
run manifest pointer pattern
manifest evidence validation
delivery evidence persistence discipline
```

The EU loop does not borrow:

```text
U.S. ETF holdings
U.S. portfolio state
U.S. report filenames as EU identity
U.S. delivery authority
U.S. valuation/funding assumptions
```

## Operating-loop design choice

MVP22 chooses option B:

```text
define but do not implement a future fresh weekly EU workflow
```

Reason: the EU repo just completed a first controlled resend and post-delivery closeout. The safer next step is to define the routine loop and manifest contract before combining fresh generation and delivery in one workflow.

## New EU routine path

```text
control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md
→ tools/write_etf_eu_routine_run_manifest.py
→ output/run_manifests/etf_eu_routine_run_manifest_<REPORT_DATE>_<RUN_ID>.json
→ output/run_manifests/latest_etf_eu_routine_run_manifest_path.txt
→ tools/validate_etf_eu_routine_run_manifest.py
```

## Authority rules

Routine weekly EU runs may produce research review and package readiness evidence.

They must not create:

```text
valuation_grade=true
funding_authority=true
portfolio_mutation=true
production_delivery_authority=true
```

Sending remains separately guarded. No send can be considered successful without persisted transport evidence. No receipt can be confirmed without receipt/closeout evidence.

## Consequence

`ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP` may close as:

```text
completed_routine_weekly_operating_loop_defined
```

The next package should be:

```text
ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN
```

MVP23 should prove that a fresh weekly EU report generation dry run can start from EU state and produce validated package/readiness artifacts without sending.
