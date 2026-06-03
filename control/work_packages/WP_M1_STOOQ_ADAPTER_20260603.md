# Work Package — M1 Stooq Adapter

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/stooq-adapter`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M1_STOOQ_ADAPTER_20260603.md`
6. `control/work_packages/WP_M1_PRICING_INTERFACE_20260603.md`

Then implement the Stooq end-of-day adapter against the common pricing interface. If the interface is not merged yet, draft against the expected interface and write a handback note.

## Current issue

The repo needs an independent free cross-check source for end-of-day prices.

## Recommended change

Implement Stooq as a provider adapter with explicit configured trading-line mappings. Do not guess symbols at runtime.

## Owned files

```text
pricing/sources/stooq.py
config/source_symbol_overrides/stooq.yml
tests/test_stooq_adapter.py
tests/fixtures/pricing/stooq/*
```

## Forbidden files

```text
pricing/sources/base.py
pricing/source_selection.py
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
config/ucits_pricing_source_policy.yml
.github/workflows/*
output/*
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

## Tasks

1. Implement the adapter against the common interface.
2. Use explicit configured source symbols only.
3. Return a typed unresolved result for missing data or provider errors.
4. Record lineage, observed date, close and currency handling.
5. Add fixture-based tests with no live network calls.
6. Do not add valuation-grade logic in this workstream.

## Definition of done

```text
- adapter returns normalized resolved or unresolved results;
- tests pass without network;
- no portfolio mutation, funding authority or delivery behavior changes.
```

## Handback instructions

Report mapped symbols, file paths, test command, result and unresolved/error behavior.
