# Work Package — M1 Agreement Gate Integration

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/agreement-gate-integration`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M1_AGREEMENT_GATE_INTEGRATION_20260603.md`

Then inspect the integrated pricing interface and at least two adapter workstreams. Do not implement this workstream until at least two adapters return normalized results or fixture-backed typed unresolved results.

## Current issue

A single observed price should not automatically become valuation-grade in the EU UCITS report pipeline.

## Recommended change

Implement an agreement gate that compares primary and cross-check source results for the same ISIN, venue/trading-line, observed date and trading currency.

## Owned files

```text
pricing/price_agreement_gate.py
tools/validate_price_agreement_gate.py
tests/test_price_agreement_gate.py
tests/fixtures/pricing/agreement_gate/*
```

May edit only during final integration:

```text
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
```

## Forbidden files

```text
.github/workflows/*
output/*
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

Do not promote any candidate to fundable.

## Tasks

1. Define statuses: `valuation_grade`, `provisional`, `blocked`.
2. Compare at least two independent source results when both are resolved.
3. Require currency match and observed-date compatibility.
4. Use configurable tolerance for close-price differences.
5. If only one source resolves, mark provisional, not valuation-grade.
6. If sources disagree or stale/mismatched data appears, mark blocked or provisional with reason.
7. Add fixture-based tests for pass, one-source-only, disagreement, stale date and currency mismatch.
8. Keep authority flags false for funding, portfolio mutation and production delivery.

## Definition of done

```text
- agreement gate produces valuation_grade, provisional or blocked;
- tests pass without network;
- valuation_grade requires configured agreement conditions;
- no pricing result creates funding authority or portfolio mutation;
- UCITS valuation artifact can consume agreement output after coordinator integration.
```

## Handback instructions

Report gate file paths, status semantics, tolerance defaults, test command, result and integration notes for valuation artifact builder.
