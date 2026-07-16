# Weekly ETF EU Review OS — Next Actions

Current priority:

```text
RUN_NEXT_ROUTINE_REPORT_AND_MONITOR_FIRST_POSITION
```

## Current production and portfolio status

```text
client_grade_v2_promoted=true
production_renderer=client_grade_v2_funded_aware
routine_production_ready=true
cap01_completed=true
model_portfolio_active=true
position_count=1
cash_eur=92900.00
invested_market_value_eur=7100.00
nav_eur=100000.00
```

The cash-only bootstrap lane is closed. Do not recreate CAP01, another allocation architecture package, or another parallel renderer.

## Current funded model position

```text
isin=IE00B5BMR087
exchange_ticker=SXR8
exchange=Xetra
trading_currency=EUR
shares=10
model_entry_price_eur=710.00
current_model_weight_pct=7.10
phase_target_weight_pct=7.50
strategic_target_weight_pct=15.00
```

This is a repository model position only. No real brokerage order was placed.

## Next routine cycle

Use:

```text
control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md
.github/workflows/run-weekly-etf-eu-routine.yml
tools/build_etf_eu_routine_report_package_v2.py
runtime/render_etf_eu_client_grade_v2_funded.py
```

The next report must use:

```text
new run_id
new report_date
new report_suffix
latest available completed-close UCITS pricing
active EU portfolio state
refreshed valuation history
current donor macro context adapted for EU use
ISIN-first plus exact trading-line identity
funded-aware Dutch-primary output
funded-aware English companion
strict v2 validation
complete rendered-page review
```

## Required position review

The next run must explicitly determine:

1. current SXR8 market value and contribution;
2. whether the SXR8 thesis and relative strength remain intact;
3. current weight versus the 7.50% first-tranche target;
4. whether any add, hold, reduce or exit action is justified;
5. whether a second tranche is allowed under fresh evidence.

No automatic second tranche is authorized.

## Candidate verification priority

### 1. Global core

```text
candidate=VWCE
strategic_target_weight_pct=50.0
first_tranche_target_weight_pct=25.0
current_status=blocked
```

Required before funding:

- exact Xetra trading-line verification;
- issuer/KID evidence reconciliation;
- broker availability;
- fresh usable EUR price;
- overlap review against SXR8;
- separate allocation decision.

### 2. Aggregate bonds

```text
candidate=EUNA
strategic_target_weight_pct=15.0
first_tranche_target_weight_pct=7.5
current_status=blocked
```

Repair the EUNA/AGGH share-class and ISIN inconsistency before any bond allocation. Do not treat different accumulating/distributing or hedged share classes as one instrument identity.

### 3. Satellites

```text
SXRV_target=7.5%
semiconductor_target=5.0%
current_status=blocked
```

Keep these as satellites. Require exact-line verification, fresh pricing and concentration review. The semiconductor line also requires an approved EUR/FX execution policy.

## Cash policy

```text
minimum_strategic_cash_reserve_pct=7.5
blocked_capacity_policy=retain_as_cash
blocked_capacity_reallocation=false
```

The current 92.90% cash weight is temporary because four target sleeves remain blocked. It must not be interpreted as a permanent bearish market call.

## Equity surface

```text
portfolio_position_count=1
current_equity_surface=active_equity_curve
```

The equity curve is now allowed because a funded model position exists. It must reconcile to `output/etf_eu_valuation_history.csv` and the current portfolio NAV.

## CAP01 closed identity

Do not reuse:

```text
work_package_id=ETF-EU-CAP01
run_id=20260716_012900
activation_id=ETF-EU-CAP01-20260716_012900
report_suffix=260716
trade_id=model-eu-2026-07-16-20260716_012900-02-SXR8-BUY
```

## Development rule

Repair concrete defects directly in the funded-aware production path. Create a new architecture package only for a material capability change. Ordinary repricing, position monitoring, candidate verification, allocation reviews and report generation are routine operations.
