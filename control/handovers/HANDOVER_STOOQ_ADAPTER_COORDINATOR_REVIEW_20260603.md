# Coordinator Review — Stooq Adapter Draft

Date: 2026-06-03  
Branch reviewed: `workstream/stooq-adapter`

## Status

```text
reviewed_as_draft_not_integrated
```

## Coordinator verdict

The Stooq adapter branch is a useful draft and the scope is clean, but it is not ready for integration yet.

Reason:

- the common pricing interface is not yet integrated into `main`;
- the Stooq adapter currently returns normalized dictionaries instead of the final shared `PriceResult` type;
- the branch is diverged from current `main`;
- the mapped Stooq symbols are explicitly provisional and need provider coverage verification before source-policy or agreement-gate use.

## Files observed in branch scope

```text
config/source_symbol_overrides/stooq.yml
pricing/sources/stooq.py
tests/fixtures/pricing/stooq/cspx_daily.csv
tests/fixtures/pricing/stooq/no_data.csv
tests/test_stooq_adapter.py
```

## Valid aspects

- Adapter uses explicit-only symbol mappings and does not guess symbols at runtime.
- Adapter has fixture-only tests with no live network calls.
- Adapter returns resolved and unresolved outcomes with source metadata and lineage.
- Adapter preserves safety flags:

```text
valuation_grade=false
portfolio_mutation=false
production_delivery=false
funding_authority=false
```

## Integration blockers before merge

1. Wait until the common pricing interface PR is merged.
2. Rebase or merge current `main` into `workstream/stooq-adapter`.
3. Replace temporary normalized dict return values with the shared `PriceResult` type.
4. Replace `fetch_close()` with or adapt it to the shared `PriceSource.fetch_eod_close(request) -> PriceResult` contract.
5. Align license class and authority tier with the shared constants from `pricing/price_result_schema.py`.
6. Decide whether unresolved rows may preserve partial close/date evidence; the current common interface rejects close values on unresolved rows.
7. Standardize repo-root imports so tests run without needing ad-hoc `PYTHONPATH=.` if the project chooses that convention.
8. Keep Stooq as cross-check/provisional evidence only until source policy and agreement gate decide how it can contribute.

## Reported validation

```text
PYTHONPATH=. pytest tests/test_stooq_adapter.py -q
3 passed
```

Plain `pytest tests/test_stooq_adapter.py -q` reportedly failed in the isolated worker environment because `pricing` was not on `PYTHONPATH`.

## No integration performed

No merge was performed. No valuation builder, validator, workflow, output, state, PDF, email, delivery or control-state behavior was changed by this review.
