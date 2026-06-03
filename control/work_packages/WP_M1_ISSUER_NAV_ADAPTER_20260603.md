# Work Package — M1 Issuer NAV Adapter

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/issuer-nav-adapter`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M1_ISSUER_NAV_ADAPTER_20260603.md`
6. `control/work_packages/WP_M1_PRICING_INTERFACE_20260603.md`

Then implement the issuer NAV/reference adapter against the common pricing interface. If the interface is not merged yet, draft against the expected interface and write a handback note.

## Current issue

Issuer references may provide useful official NAV/reference data, but NAV is not the same primitive as an exchange trading-line close.

## Recommended change

Implement issuer NAV/reference retrieval as a separate adapter with a distinct authority tier and clear lineage.

## Owned files

```text
pricing/sources/issuer_nav.py
tests/test_issuer_nav_adapter.py
tests/fixtures/pricing/issuer_nav/*
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
2. Keep issuer NAV distinct from exchange close in the authority tier.
3. Return typed unresolved results for missing NAV, date, currency or parsing uncertainty.
4. Add fixture-based tests with no live network calls.
5. Do not add valuation-grade logic here.

## Definition of done

```text
- adapter returns normalized resolved or unresolved results;
- NAV and market close are not conflated;
- tests pass without network;
- no portfolio mutation, funding authority or delivery behavior changes.
```

## Handback instructions

Report adapter path, fixture paths, metadata, test command, result and issuer-data limitations.
