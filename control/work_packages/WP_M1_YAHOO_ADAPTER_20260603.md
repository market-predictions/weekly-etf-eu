# Work Package — M1 Yahoo Adapter

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/yahoo-adapter`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M1_YAHOO_ADAPTER_20260603.md`
6. `control/work_packages/WP_M1_PRICING_INTERFACE_20260603.md`

Then implement the Yahoo adapter against the common pricing interface. If the interface is not merged yet, draft against the expected interface and write a handback note.

## Current issue

Yahoo already returns practical close observations, but it should be a fallback/provisional source rather than the only path to valuation-grade pricing.

## Recommended change

Refactor Yahoo close retrieval into a typed adapter with explicit status, licence metadata, authority tier and lineage.

## Owned files

```text
pricing/sources/yahoo.py
tests/test_yahoo_adapter.py
tests/fixtures/pricing/yahoo/*
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
2. Mark Yahoo as fallback/provisional in metadata.
3. Return typed unresolved results for missing history, close, date, currency or provider errors.
4. Add fixture-based tests with no live network calls.
5. Do not add valuation-grade logic here.

## Definition of done

```text
- adapter returns normalized resolved or unresolved results;
- tests pass without network;
- no portfolio mutation, funding authority or delivery behavior changes.
```

## Handback instructions

Report adapter path, fixture paths, metadata, test command, result and limitations.
