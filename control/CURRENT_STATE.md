# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-07-29
repository=market-predictions/weekly-etf-eu
working_branch=sync/donor-report-parity
pull_request=66
operating_mode=routine_production_plus_non_authoritative_sync_cutover_shadow
selected_next_action=REVIEW_WP_SYNC_00_08_DRAFT_PR_WITHOUT_ACTIVATION
```

The routine production system remains available. The synchronization work in PR #66 is an isolated shadow architecture and has not replaced the official portfolio, trade ledger, production report or routine delivery workflow.

## Official EU model portfolio

Authoritative source:

```text
output/etf_eu_portfolio_state.json
```

Current accepted state:

```text
starting_capital_eur=100000.00
nav_eur=99756.76
cash_eur=60439.44
invested_market_value_eur=39317.32
position_count=3
model_portfolio_only=true
real_broker_execution=false
```

| Position | ISIN | Shares | Model price | Market value | Weight | Official action |
|---|---|---:|---:|---:|---:|---|
| VWCE | IE00BK5BQT80 | 151 | €164.28 | €24,806.28 | 24.866766% | Hold |
| EUNA | IE00BDBRDM35 | 1,526 | €4.8919 | €7,465.04 | 7.483242% | Hold |
| SXR8 | IE00B5BMR087 | 10 | €704.60 | €7,046.00 | 7.063180% | Hold; no second tranche |

Official state and ledger preservation evidence:

```text
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
trade_ledger_record_count=4
portfolio_mutation_performed=false
ledger_write_performed=false
```

## Shared donor contract

The donor shared-state contract is merged and immutable:

```text
contract_release_id=weekly_etf_shared_contract_v1_0_0
donor_repository=market-predictions/weekly-etf
donor_commit_sha=455201b4736dda41df07644d78b6797282a29fc7
mutable_donor_branch_allowed=false
```

All EU synchronization, allocator, replay and report workflows consume this exact commit.

## Validated Stage-1 shadow

The preferred policy-constrained simulation remains:

| Component | Shadow result |
|---|---:|
| VVSM | 156 simulated shares; 14.804530% |
| LOCK | 995 simulated shares; 10.187710% |
| VWCE | Retain 151 shares |
| EUNA | Retain 1,526 shares |
| SXR8 | Retain 10 shares |
| Gross turnover | €24,931.45; 24.992241% NAV |
| Estimated friction | €24.93 |
| Projected cash | €35,483.06; 35.569579% NAV |
| Resulting position count | 5 |

This is a shadow target only:

```text
stage_1_activation_authorized=false
official_state_applied=false
execution_receipt_exists=false
executable_trade_intents=[]
```

Registry expansion cannot silently reopen Stage-1 selection. The Stage-1 candidate set is explicitly limited to AI compute/semiconductors and cybersecurity until its policy is deliberately versioned.

## EUNA risk-budget decision

The accepted shadow classification is:

```text
role=low_volatility_carry_diversifier_not_reliable_equity_hedge
stage_1_action=hold_current_position_no_add_no_sale
stage_2_automatic_sale=false
stage_2_funding_priority=third
```

EUNA is not available as a Stage-2 funding source under the current review.

## Stage-2 readiness

The initial capacity-analysis destination is IXUA / developed markets outside the United States.

```text
donor_target_weight_pct_nav=24.66
stage_2_maximum_weight_pct_nav=15.00
cash_source_capacity_pct_nav=10.569579
sxr8_source_use_pct_nav=4.430421
projected_cash_floor_pct_nav=25.00
euna_source_use_pct_nav=0.00
```

Stage 2 is correctly blocked. A donor target and a fresh donor add signal are separate authorities. The current donor direction is `hold_or_monitor`, so:

```text
donor_add_direction_pass=false
donor_add_direction_not_confirmed=true
```

Additional blockers include missing official Stage-1 state and receipt, incomplete IXUA document/valuation/tradability evidence and absent Stage-2 authorization. No executable Stage-2 intents exist.

## Executive sister report

The synchronized Dutch and English shadow reports preserve the donor section/table contract and render as matching 11-page executive reports.

Validated source:

```text
workflow_run_id=30410361517
source_head_sha=d33169fa513e22ac9197efe4fab9857ebaa6f85f
artifact_id=8708156245
artifact_digest=sha256:4ae7cdfb0335587a6eb564434b40ef914775913c76dd3a9bc7b2b21799875b36
```

The shadow report is not the official production report.

## CID delivery validation

A self-addressed shadow delivery test completed successfully:

```text
shadow_run_id=wp_sync_08_cid_20260729_002500
delivery_workflow_run_id=30410951339
smtp_transport_success=true
sent_match_observed=true
inbox_match_observed=true
attachment_count=4
inline_image_count=1
cid_reference_count=1
```

The Gmail message preserves the four expected HTML/PDF attachments and the inline 57,780-byte PNG chart with a matching Content-ID.

Privacy-minimal receipt evidence:

```text
control/evidence/etf_eu_shadow_cid_mailbox_receipt_wp_sync_08_cid_20260729_002500.json
```

This is shadow transport evidence only; it is not a production report-delivery receipt.

## Blocked activation package

The cutover-readiness package is complete and valid:

```text
package_id=ETF-EU-SYNC-CUTOVER-READINESS-20260729
workflow_run_id=30411531406
artifact_id=8708563958
artifact_digest=sha256:cb3880c366a18b066ca8895dbd5da9c213ca580da2121376f59f556b0a4b0ed4
status=blocked_not_activation_ready
activation_ready=false
package_blocker_count=27
executable_trade_intents=[]
```

The package binds the immutable donor contract, validated EU design, official pre-cutover state hashes, Stage-1 simulation, Stage-2 blocked readiness, product-evidence gaps, redacted Gmail receipt and state-oriented rollback boundary.

## Authority boundaries

```text
model_portfolio_only=true
real_broker_execution=false
valuation_grade_for_new_lines=false
funding_authority=false
portfolio_mutation=false
ledger_write=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
```

PR #66 must remain a draft until its architecture and evidence package are reviewed. Merging the shadow architecture, activating Stage 1 and replacing the production report are three separate decisions.
