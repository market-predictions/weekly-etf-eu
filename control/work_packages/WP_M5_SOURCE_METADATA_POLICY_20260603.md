# Work Package — M5 Source Metadata Policy

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/source-metadata-policy`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M5_SOURCE_METADATA_POLICY_20260603.md`

Then implement documentation and tests for source metadata categories. Do not approve or reject any provider beyond the documented metadata.

## Current issue

The repo needs consistent source metadata so free, fallback, reference and future paid sources can be selected by policy rather than hardcoded logic.

## Recommended change

Create a source metadata register and a small helper that can filter sources by declared policy mode.

## Owned files

```text
control/DATA_SOURCE_METADATA.md
control/CHANGELOG.md
pricing/source_metadata_policy.py
tests/test_source_metadata_policy.py
```

## Forbidden files

```text
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
.github/workflows/*
output/*
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

Do not edit `config/ucits_pricing_source_policy.yml` unless the coordinator approves.

## Tasks

1. Create `control/DATA_SOURCE_METADATA.md`.
2. Define metadata categories for source type, usage mode, authority tier and review status.
3. Add a helper that filters sources based on declared policy mode.
4. Add fixture-based tests only.
5. Record unresolved source-review questions without making external claims.

## Definition of done

```text
- source metadata register exists;
- metadata categories align with the pricing interface;
- tests pass without network;
- no production workflow, portfolio state or delivery behavior changes.
```

## Handback instructions

Report files created, metadata categories, unresolved review questions, test command and result.
