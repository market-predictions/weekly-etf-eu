# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-06
repository=market-predictions/weekly-etf-eu
working_branch=agent/etf-eu-client-grade-release-remediation
pull_request=80
operating_mode=client_grade_release_remediation_no_send
implementation_status=IMPLEMENTATION_IN_PROGRESS
assurance_status=GOVERNANCE_INDETERMINATE
selected_next_action=PASS_BOUNDARY_AND_LINEAGE_CI_THEN_BUILD_REVIEWABLE_ETF_EU_CANDIDATE
```

The project is repairing two distinct defects before another Weekly ETF EU report may be reviewed or sent:

1. inherited Weekly FX production assets were present in the ETF EU repository and could surface unrelated FX output;
2. portfolio reconstruction could be arithmetically consistent without proving lineage to the protected ETF EU portfolio and an explicit allocation decision.

No report generated during this remediation is approved for delivery. No current email delivery or independent receipt has been claimed.

## Product boundary

```text
product=weekly_etf_eu
misplaced_fx_scheduler=removed_on_candidate_branch
misplaced_fx_generator=removed_on_candidate_branch
daily_fx_instructions=removed_on_candidate_branch
daily_outputs_fx_tree=removed_on_candidate_branch
mt5_fx_tree=removed_on_candidate_branch
repository_boundary_ci=implemented_pending_green_receipt
```

The removed assets were inherited TwelveData/FX scaffolding, including `prediction.py`, `TWELVEDATA_API_KEY`, DailyTradeBias material and current FX ranking outputs. `control/REPOSITORY_PRODUCT_BOUNDARY.md` defines the product boundary and `tools/validate_etf_eu_repository_boundary.py` fails when FX production assets or execution tokens reappear.

The same inherited contamination was found in the Weekly ETF donor. It is being removed separately in Weekly ETF PR #119 so the donor can no longer regenerate the wrong product either.

## Official protected model portfolio

Source of truth:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
```

Current protected state:

| Ticker | Shares | Current recorded weight |
|---|---:|---:|
| VWCE | 151 | 24.8668% |
| EUNA | 1,526 | 7.4832% |
| SXR8 | 10 | 7.0632% |
| L0CK | 934 | 10.2560% |

```text
starting_capital_eur=100000.00
cash_eur=50208.40
invested_market_value_eur=49548.36
nav_eur=99756.76
position_count=4
model_portfolio_only=true
real_broker_execution=false
activation_id=ETF-EU-STAGE1-2026-08-04-20260804_STAGE1_30947965670_1
```

L0CK was added through the explicit model-only Stage-1 allocation decision:

```text
output/activation/etf_eu_stage1_allocation_decision_20260804_STAGE1_30947965670_1.json
```

VVSM remains evaluated and monitored but unfunded because it was not currently promoted by the donor decision framework.

## Allocation authority correction

The earlier remediation draft proposed a universal maximum position weight of 50% and a mandatory cash reserve of 35%. Comparison with the authoritative Weekly ETF donor rules showed that these percentages are not donor policy and must not be treated as such.

The donor's `75` threshold is a minimum pricing-coverage percentage, not a portfolio concentration rule.

The active ETF EU release policy is now:

```text
policy_id=ETF_EU_RELEASE_LINEAGE_POLICY_V2
hard_maximum_position_weight_pct=null
mandatory_cash_floor_pct=null
allocation_validity=protected_state_plus_explicit_authorized_mutation
```

For valuation-only report generation:

- ticker roster, exact shares and cash must remain identical to protected state;
- any share or cash mutation requires an explicit allocation-decision artifact;
- NAV, market values, shares × price and stated weights must reconcile;
- concentration is disclosed and re-underwritten, not accepted or rejected by an invented percentage.

This means an allocator-created 75% VWCE state fails because it changes protected shares/cash without authority. A hypothetical market-driven 75% weight with unchanged shares and cash is surfaced for underwriting review rather than automatically blocked by an unsupported cap.

## Pricing status

The completed-close layer retains the two-provider, same-date and exact-identity requirements for every funded position. A rollover defect was found in the Xetra adapter: after the next session began, a valid prior-session `closingPricePrevTradingDay` was rejected. The candidate branch now resolves that immediate previous-session rollover while remaining fail-closed for stale dates.

A fresh current package has not yet completed the full pricing, report, visual and assurance sequence after this correction.

## Report and release status

```text
reviewable_four_file_candidate=false
machine_validation_complete=false
visual_review_complete=false
user_review_complete=false
delivery_queue_created=false
governance_pass_pre_send=false
smtp_transport_success=false
independent_receipt_confirmed=false
delivery_confirmed=false
```

The target output remains exactly:

```text
Dutch HTML
Dutch PDF
English HTML
English PDF
```

The current remediation PR cannot send. Guarded transport remains a later step after a reviewable package exists and the user approves it.

## Maturity comparison

The detailed comparison with Weekly ETF is recorded in:

```text
control/ETF_EU_MATURITY_GAP_REVIEW_2026-08-06.md
```

Current layer status:

| Layer | Status |
|---|---|
| Decision framework | authority precedence corrected; one canonical weekly EU underwriting decision still needed |
| Input/state contract | protected-state lineage implemented; immutable run-input manifest still needed |
| Output contract | four-file target established; canonical renderer consolidation still needed |
| Operational runbook | FX path removed; historical workflow sprawl still needs retirement |
| Governance/release assurance | policy-bound pre-send gate implemented but not yet green end to end |
| Delivery/receipt | current remediated package unsent and unconfirmed |

## Authority boundary

```text
portfolio_mutation=false
ledger_write=false
real_broker_execution=false
email_delivery=false
delivery_authority=false
receipt_confirmed=false
```

The highest honest status before the current CI and package cycle complete is `IMPLEMENTATION_IN_PROGRESS`. A rendered artifact alone must not be treated as a release candidate or delivery receipt.
