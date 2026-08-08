# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-08
repository=market-predictions/weekly-etf-eu
working_branch=agent/etf-eu-client-grade-release-remediation
pull_request=80
operating_mode=client_grade_release_remediation_no_send
implementation_status=RELEASE_CANDIDATE_READY_FOR_PRICING_LINEAGE
assurance_status=GOVERNANCE_INDETERMINATE_FOR_FULL_REPORT
selected_next_action=COMPLETE_CURRENT_FRESH_PACKAGE_THEN_INDEPENDENTLY_ASSURE_REVIEWABLE_CANDIDATE
```

The highest-priority pricing-lineage blocker has been resolved at implementation level. Historical report replay no longer depends on a rolling live `previous close` field or on a later mutable adjusted price series.

No current report is approved for delivery. No email transport or independent receipt is claimed.

## Product boundary

The ETF EU remediation branch is product-pure:

```text
product=weekly_etf_eu
misplaced_fx_scheduler=removed
misplaced_fx_generator=removed
daily_fx_instructions=removed
daily_outputs_fx_tree=removed
mt5_fx_tree=removed
repository_boundary_ci=PASS
```

The prior `.github/workflows/generate_predictions.yml` path was an FX workflow that invoked `prediction.py` and could surface Weekly FX output from the ETF EU repository. It is absent on the remediation branch. Repository-boundary CI is green.

## Protected model portfolio authority

Authoritative state:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
```

Current protected model positions:

| Ticker | Shares |
|---|---:|
| VWCE | 151 |
| EUNA | 1,526 |
| SXR8 | 10 |
| L0CK | 934 |

```text
cash_eur=50208.40
position_count=4
model_portfolio_only=true
real_broker_execution=false
activation_id=ETF-EU-STAGE1-2026-08-04-20260804_STAGE1_30947965670_1
```

VVSM remains monitored and unfunded.

## Allocation authority correction

The earlier remediation draft's universal 50% position cap and mandatory 35% cash floor were rejected after comparison with the mature Weekly ETF donor rules.

Current policy:

```text
policy_id=ETF_EU_RELEASE_LINEAGE_POLICY_V2
hard_maximum_position_weight_pct=null
mandatory_cash_floor_pct=null
allocation_validity=protected_state_plus_explicit_authorized_mutation
```

A valuation-only report must preserve the protected ticker roster, exact shares and cash. Any mutation requires an explicit allocation-decision artifact. Concentration is an underwriting observation and disclosure issue unless an explicit later decision establishes a hard cap.

Therefore the previously observed ~75% VWCE reconstruction is invalid because it changed shares and cash without authority, not because 75% crossed an invented 50% threshold.

## Replay-safe pricing lineage

Work package:

```text
ETF-EU-WP-SYNC-11B
status=RELEASE_CANDIDATE_READY
```

Original accepted 2026-08-05 evidence was recovered from the still-retained GitHub Actions artifact:

```text
source_workflow_run_id=31051399761
source_run_id=20260805_31051399761_1
source_workflow_head_sha=476579ecc0644250d7d12a8f69784a279118d389
actions_artifact_id=8948609199
actions_artifact_digest=sha256:631f90f24caabc271b1d290b519adf5c3e667cb717f35563f522d030cb49c55a
qualification_member_sha256=02ad0fa5dd431eebadf73c370b6ab9fdc85a570332667a26234ad0d1758611d4
```

Original accepted funded closes:

| Ticker | Close | Providers | Spread |
|---|---:|---|---:|
| VWCE | 168.04 | Börse Frankfurt + Yahoo | 0.0% |
| EUNA | 4.9116 | Börse Frankfurt + Yahoo | 0.0% |
| SXR8 | 722.42 | Börse Frankfurt + Yahoo | 0.0% |
| L0CK | 10.932 | Börse Frankfurt + Yahoo | 0.0% |

The evidence is preserved in:

```text
state/price_evidence_cache/ucits_close_evidence_2026-08-05.json
```

Replay is exact-date and identity bound. It rejects report-date, basket, ticker, ISIN, MIC, currency, provider-set, provider-symbol, tolerance or provenance mismatches.

Independent implementation CI:

```text
workflow=Validate ETF EU replay-safe historical pricing
workflow_run_id=31254153417
job_id=93094895139
conclusion=success
funded_two_provider_replay=4/4
funded_identity_anchor_replay=4/4
```

The public Börse Frankfurt `price_history` endpoint was also tested. It returned HTTP 200 with an empty object for the tested ETF requests on hosted GitHub runners, so it is not treated as a durable sole replay source. The two-provider gate was not weakened.

## Current CI state

For the replay-safe commit line, the following are green:

```text
Validate ETF EU replay-safe historical pricing=PASS
Validate ETF EU multi-provider close-price engine=PASS
Validate Weekly ETF EU product boundary=PASS
Validate ETF EU release assurance fixtures=PASS
Validate ETF EU activated action-row contract=PASS
```

The broader fresh governed candidate build is executing separately and must complete before the project can present a client report for review.

## Client-grade release status

```text
product_boundary_validation=PASS
allocation_lineage_architecture=PASS
historical_pricing_replay=PASS
funded_two_provider_replay=4/4
fresh_current_package=IN_PROGRESS
four_file_candidate=NOT_YET_CONFIRMED
machine_report_validation=NOT_YET_CONFIRMED
visual_review=NOT_YET_CONFIRMED
independent_full_release_assurance=NOT_YET_RUN_ON_FINAL_CANDIDATE
user_review=NOT_YET_REQUESTED
email_delivery=false
independent_receipt_confirmed=false
```

## Maturity gaps after current P1 work

1. Finish one fresh governed ETF EU candidate using the repaired product, allocation and pricing lineage.
2. Bind replay-safe/current pricing evidence into one immutable run-input manifest.
3. Independently reconstruct report/state/pricing equality and visual parity.
4. Consolidate historical generation and send workflows to a small production allowlist.
5. Designate one canonical production renderer.
6. Present the exact Dutch/English candidate to the user before delivery authority exists.
7. After explicit approval, execute guarded transport and independently confirm inbox receipt/attachment identity.

## Authority boundary

```text
portfolio_mutation=false
ledger_write=false
real_broker_execution=false
email_delivery=false
delivery_authority=false
receipt_confirmed=false
```
