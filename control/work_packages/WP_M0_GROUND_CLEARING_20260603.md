# Work Package — M0 Ground-Clearing

Date: 2026-06-03  
Repository: `market-predictions/weekly-etf-eu`  
Branch: `workstream/m0-ground-clearing`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M0_GROUND_CLEARING_20260603.md`

Then perform the M0 ground-clearing tasks only. Keep the work time-boxed and non-destructive.

## Current issue

The repo still contains inherited U.S./intraday artifacts and duplicate old files that make the EU product harder to reason about.

## Root cause

The EU repo was cloned from the U.S. ETF repo. Historical files are useful provenance, but active paths should not imply that U.S. intraday/ICT logic is EU UCITS authority.

## Recommended change

Archive or quarantine clearly inactive inherited files; pin dependencies; document the canonical workflow. Do not delete useful history.

## Owned files / paths

This workstream may edit:

```text
README.md
requirements.txt
archive/README.md
archive/legacy_us_intraday/*
archive/legacy_senders/*
.gitignore
```

It may move/archive inactive files only when no active workflow imports them.

## Forbidden files

Do not edit:

```text
pricing/sources/*
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
config/ucits_pricing_source_policy.yml
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
.github/workflows/*
output/*
```

Do not remove run-queue triggers unless the coordinator explicitly approves a replacement trigger path.

## Tasks

1. Audit active imports before moving any file.
2. Quarantine `prediction.py` only if no active EU workflow imports it.
3. Archive duplicate sender variants, but keep exactly one active sender file if still needed.
4. Pin missing dependencies used by active workflows, especially `pyyaml` and `yfinance`.
5. Add or update a short README that identifies the canonical EU workflow and bootstrap validation entry point.
6. Add `.gitignore` entries for future run-queue clutter only if this does not break the existing trigger mechanism.

## Definition of done

```text
- CI/bootstrap validation still passes or local static validation shows no broken imports.
- Active EU pipeline no longer imports quarantined intraday code.
- requirements.txt contains all active runtime dependencies and pins versions.
- README explains the canonical workflow in one page or less.
- No pricing authority, funding authority, portfolio mutation or delivery behavior changed.
```

## Handback instructions

At completion, write a short handover note listing:

```text
- files moved or archived;
- dependency changes;
- workflow/README changes;
- validation evidence;
- any cleanup deferred to coordinator.
```
