# Work Package — M1 Boerse Frankfurt / Xetra Adapter

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/boerse-frankfurt-adapter`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M1_BOERSE_FRANKFURT_ADAPTER_20260603.md`
6. `control/work_packages/WP_M1_PRICING_INTERFACE_20260603.md`

Then implement the Boerse Frankfurt / Xetra end-of-day adapter against the common pricing interface. If the interface is not merged yet, draft against the expected interface and write a handback note.

## Current issue

The repo needs an ISIN-first source candidate for Xetra trading lines instead of continuing fragile page-scraping experiments.

## Recommended change

Implement a provider adapter that uses ISIN plus venue/MIC inputs, records source lineage, and degrades cleanly to unresolved results when the provider response is unavailable or changes shape.

## Owned files

```text
pricing/sources/boerse_frankfurt.py
config/source_symbol_overrides/boerse_frankfurt.yml
tests/test_boerse_frankfurt_adapter.py
tests/fixtures/pricing/boerse_frankfurt/*
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
2. Use ISIN and venue/MIC inputs where possible.
3. Return typed unresolved results on provider errors, schema drift, missing close, missing date or currency uncertainty.
4. Tag the source as an undocumented/free source until licensing is confirmed.
5. Add fixture-based tests with no live network calls.
6. Do not create valuation-grade logic here.

## Definition of done

```text
- adapter returns normalized resolved or unresolved results;
- tests pass without network;
- license/authority metadata is present;
- no portfolio mutation, funding authority or delivery behavior changes.
```

## Handback instructions

Report endpoint assumptions, file paths, fixture paths, test command, result and unresolved/error behavior.
