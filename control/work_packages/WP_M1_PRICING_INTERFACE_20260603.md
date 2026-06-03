# Work Package — M1 Pricing Interface

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/pricing-interface`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M1_PRICING_INTERFACE_20260603.md`

Then implement only the common pricing interface. Do not implement provider adapters in this chat.

## Current issue

The pricing layer has provider-specific diagnostics, but no shared typed contract for end-of-day close retrieval.

## Recommended change

Create a small typed pricing spine with:

- one normalized result object;
- one common provider interface;
- one config-driven selection helper;
- tests with fake providers only.

The result object should include identity, observed date, close, currency, provider name, status, licence category, authority tier, lineage, errors and resolved/unresolved state.

## Owned files

```text
pricing/price_result_schema.py
pricing/source_selection.py
pricing/sources/base.py
pricing/sources/__init__.py
pricing/README.md
tests/test_pricing_interface.py
tests/fixtures/pricing/*
```

## Forbidden files

```text
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
config/ucits_pricing_source_policy.yml
.github/workflows/*
output/*
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

## Tasks

1. Define the normalized result object.
2. Define the common provider interface.
3. Define standard success and unresolved statuses.
4. Define standard licence and authority category strings.
5. Add fake-provider tests only. No network calls.
6. Document how adapter chats should implement the interface.

## Definition of done

```text
- common pricing interface exists;
- fake-provider tests pass without network;
- config-driven selection is possible;
- resolved and unresolved provider responses are represented;
- no workflow, portfolio state or delivery behavior changes.
```

## Handback instructions

Report the new file paths, required fields, test command, result and compatibility notes.
