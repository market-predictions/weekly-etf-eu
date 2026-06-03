# Work Package — Coordinator / Parallel Pricing Spine

Date: 2026-06-03  
Repository: `market-predictions/weekly-etf-eu`  
Branch: `workstream/coordinator-pricing-spine`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_COORDINATOR_PARALLEL_PRICING_SPINE_20260603.md`

Then coordinate the parallel workstreams. Do not implement adapter logic yourself unless needed for integration.

## Current issue

The EU repo risks becoming a pile of pricing diagnostics and validators without one clean pricing spine. Parallel work can help, but only if file ownership, merge order, authority boundaries and validation are explicit.

## Root cause

The repo was cloned from the U.S. ETF system and has accumulated scaffolding around pricing-source diagnostics. The previous Yahoo temporary fallback handover would solve a local artifact problem but would not create a robust free-now / paid-later pricing architecture.

## Recommended change

Coordinate a new pricing architecture based on:

```text
PriceSource adapter interface
PriceResult typed result
source policy driven ordering
license_class as first-class metadata
agreement gate before valuation_grade
Yahoo as tertiary/provisional fallback, not sole valuation authority
```

## Owned files

This workstream owns:

```text
control/PARALLEL_WORKSTREAM_PLAN_20260603.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
control/CHANGELOG.md
control/handovers/*parallel*pricing*spine*.md
```

## Forbidden files unless integrating completed branches

Do not casually edit:

```text
pricing/sources/*
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
.github/workflows/*
output/*
```

## Tasks

1. Keep workstream ownership clean.
2. Review each workstream branch or handover before merge.
3. Verify no pricing workstream creates funding authority, portfolio mutation or production delivery.
4. Merge in the order defined in `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`.
5. After each successful integration, update `control/CHANGELOG.md`.
6. Only after integration update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`.
7. Write a handover file if work pauses.

## Definition of done

This coordinator workstream is done when:

```text
- all active workstreams have instruction files;
- branch/file ownership is explicit;
- merge order is documented;
- at least the PriceSource interface and two adapters have been integrated or queued for integration;
- no production delivery or portfolio mutation has been enabled;
- CURRENT_STATE and NEXT_ACTIONS reflect the new pricing-spine direction.
```

## Authority rules

Never claim delivery succeeded unless a delivery manifest or receipt exists. During this phase, no delivery should occur.
