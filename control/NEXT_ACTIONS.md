# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
GENERATE_AND_VISUALLY_REVIEW_FUNDED_AWARE_THREE_POSITION_ROUTINE_REPORT
```

## Completed state

```text
broker_neutral_registry_reconciliation=true
broker_neutral_review_run_id=20260716_205500
review_validation_passed=true
model_activation_applied=true
activation_validation_passed=true
position_count=3
cash_eur=60439.44
invested_market_value_eur=39577.16
nav_eur=100016.60
real_broker_execution=false
production_delivery=false
```

The cash-only bootstrap lane, CAP01 and the broker-neutral first-tranche activation are closed. Do not recreate them.

## Current positions

| Ticker | Role | Shares | Value | Weight | Current action |
|---|---|---:|---:|---:|---|
| VWCE | Global core | 151 | €24,963.32 | 24.959177% | Hold after first tranche |
| EUNA | Aggregate-bond stabiliser | 1,526 | €7,497.24 | 7.495996% | Hold after first tranche |
| SXR8 | U.S. equity overweight | 10 | €7,116.60 | 7.115419% | Hold; no second tranche |

Cash remains €60,439.44. It represents strategic reserve, blocked satellite capacity and later-tranche capacity—not a permanent bearish allocation call.

## Immediate next production cycle

Create a new run identity and produce a current funded-aware report from the official three-position state.

Required sequence:

```text
1. obtain or retain transparent current exact-line prices with explicit dates;
2. read output/etf_eu_portfolio_state.json as quantity authority;
3. read output/etf_eu_valuation_history.csv as equity-curve authority;
4. refresh donor macro context from market-predictions/weekly-etf and adapt it for EU use;
5. build normalized funded-aware report state;
6. render Dutch-primary HTML/PDF and English-companion HTML/PDF;
7. run strict client-grade v2 validation;
8. inspect every PDF page for clipping, overlap, stale wording and table readability;
9. create a review/closeout manifest;
10. do not send unless the user separately authorizes delivery.
```

The report must visibly include:

```text
VWCE 151 shares
EUNA 1526 shares
SXR8 10 shares
cash EUR 60,439.44
NAV EUR 100,016.60
whole-share and model-only disclosures
price dates and non-valuation-grade source boundaries
active equity curve
```

## Monitoring after report generation

For each routine cycle determine separately:

1. whether VWCE remains a valid global-core holding;
2. whether EUNA continues to provide the intended stabilising role;
3. whether SXR8 remains a justified U.S. overweight;
4. position contribution and relative strength since activation;
5. overlap between VWCE's embedded U.S. exposure and direct SXR8 exposure;
6. whether cash remains blocked capacity or should receive a separately authorized tranche.

No automatic add, reduce, exit or second tranche is allowed.

## Candidate development after the report

### SXRV

```text
strategic_target_weight_pct=7.5
current_status=blocked_not_funded
```

Require exact-line identity, fresh EUR pricing, concentration/overlap review and a separate allocation decision.

### Semiconductor satellite

```text
strategic_target_weight_pct=5.0
current_status=blocked_not_funded
```

Require verified UCITS exchange line, fresh pricing, concentration review and an approved EUR/FX model-execution policy. Broker permission is not a model gate.

## Broker and delivery boundaries

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
real_order_authority=false
production_delivery_authority=false
```

Only a contemplated real order may open the optional broker adapter for contract lookup, account eligibility, costs, routing and preview.

Only explicit delivery authority may open the guarded send path. Delivery success may be claimed only when the transport layer creates a real receipt or manifest and delayed receipt verification confirms the expected attachments.

## Current evidence

```text
control/decisions/ETF_EU_BROKER_NEUTRAL_FIRST_TRANCHE_ACTIVATION_DECISION_20260716.md
output/runtime/etf_eu_broker_neutral_allocation_review_20260716_205500.json
output/quality/etf_eu_broker_neutral_allocation_review_validation_20260716_205500.json
output/runtime/etf_eu_broker_neutral_model_activation_result_20260716_205500.json
output/quality/etf_eu_broker_neutral_model_activation_validation_20260716_205500.json
output/run_manifests/etf_eu_broker_neutral_model_activation_manifest_20260716_205500.json
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
output/etf_eu_valuation_history.csv
```

## Closed identities

Do not reuse:

```text
run_id=20260716_012900
review_run_id=20260716_092600
broker_neutral_review_run_id=20260716_205500
activation_id=ETF-EU-BROKER-NEUTRAL-20260716_205500
report_suffix=260716
```

## Development rule

Repair concrete funded-aware production defects directly. Create a new architecture package only for a material capability change. The current work is routine report generation, visual review and position monitoring—not another architecture cycle.
