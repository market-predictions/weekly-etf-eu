# Work Package — M2 First Report Integration

Date: 2026-06-03
Repository: `market-predictions/weekly-etf-eu`
Branch: `workstream/first-report-integration`

## Fresh-chat prompt

Continue in `market-predictions/weekly-etf-eu`.

Read from GitHub in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PARALLEL_WORKSTREAM_PLAN_20260603.md`
5. `control/work_packages/WP_M2_FIRST_REPORT_INTEGRATION_20260603.md`

Then inspect the integrated pricing interface, adapter outputs and agreement gate. Do not implement this workstream until the coordinator confirms agreement-gate integration exists.

## Current issue

The EU repo can render candidate skeletons, but not yet a real priced EU UCITS report row driven by an agreed end-of-day price.

## Recommended change

Wire normalized pricing and agreement-gate output into the UCITS valuation artifact and then into the Dutch-first candidate report surface.

## Owned files

```text
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
runtime/render_etf_eu_report.py
tools/validate_etf_eu_candidate_report.py
tests/test_ucits_valuation_prices.py
tests/test_etf_eu_report_pricing_surface.py
```

May edit with coordinator approval:

```text
.github/workflows/send-weekly-etf-eu-report.yml
config/ucits_pricing_source_policy.yml
```

## Forbidden files

```text
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
production delivery workflows
SMTP/email settings
```

## Tasks

1. Consume agreement-gate outputs in the valuation artifact.
2. Allow rows to surface as valuation-grade, provisional or blocked.
3. Show source, observed date, close, currency, source agreement status and staleness in the report.
4. Keep cash-only state unchanged unless a separate funding/promotion contract exists.
5. Ensure the Dutch report remains client-safe and does not claim funded holdings if there are none.
6. Validate no production delivery, PDF generation or email send is triggered.

## Definition of done

```text
- at least one verified UCITS candidate can display a real priced row when agreement-gate data exists;
- report distinguishes priced candidates from funded holdings;
- cash-only portfolio state remains unchanged;
- no funding authority, portfolio mutation or production delivery is created;
- validators pass.
```

## Handback instructions

Report files changed, valuation statuses supported, report-surface changes, validation command, result and any remaining blockers before production delivery can ever be considered.
