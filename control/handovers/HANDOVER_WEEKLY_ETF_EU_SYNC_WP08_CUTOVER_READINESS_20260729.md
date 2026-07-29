# Handover — Weekly ETF EU synchronization WP-SYNC-08

**Date:** 2026-07-29  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/donor-report-parity`  
**Pull request:** #66  
**Status:** presentable shadow architecture; blocked for activation

## 1. Current issue resolved

The Stage-2 validator originally expected IXUA to carry a donor `add_candidate` direction because the donor portfolio has a 24.66% developed-ex-U.S. target.

That interpretation was wrong. The donor already holds the exposure and currently emits `hold_or_monitor`. A donor target and a fresh donor add instruction are separate authorities.

## 2. Root cause

Two independent contract issues were found:

1. Stage-2 validation collapsed target presence and fresh-add direction.
2. The synchronization artifact stores authority under a nested `authority` object, while the EUNA artifact stores authority flags at the top level. The initial Stage-2 builder assumed one shape for both.

Neither issue justified weakening an authority gate.

## 3. Implemented correction

### Donor action reconciliation

The Stage-2 policy and validator now require:

```text
donor_target_present=true
donor_fresh_add_direction=false
donor_add_direction_not_confirmed=true
```

IXUA remains a valid mapping and capacity-analysis destination, but it cannot enter an activation package without a genuine donor add signal or a separate EU strategic-migration decision.

### Authority contract normalization

`runtime/build_etf_eu_stage_2_readiness_v2.py` verifies the nested synchronization authority flags and normalizes them to top-level false values solely for the existing builder contract. It rejects any authority escalation.

### Result

The complete chain is green:

```text
strategy synchronization run=30410361524
cutover product evidence run=30410361523
target allocator run=30410361572
transition replay + EUNA + Stage-2 run=30410361535
allocator report run=30410361517
CID dry-run run=30410361567
```

## 4. Live CID delivery

### First attempt

The first queue-triggered run failed before SMTP because `git diff-tree` could not discover the queue file in a shallow checkout.

Exact failure:

```text
ETF_EU_SHADOW_CID_REQUEST_MISSING
```

No email was sent in that attempt.

### Corrective change

The send workflow now:

- checks out full history;
- finds the newest queue file directly;
- verifies that the queue file was created by the triggering commit;
- retains the existing source-run, source-SHA, self-recipient and confirmation gates.

### Successful attempt

```text
shadow_run_id=wp_sync_08_cid_20260729_002500
source_report_run_id=30410361517
source_report_head_sha=d33169fa513e22ac9197efe4fab9857ebaa6f85f
delivery_workflow_run_id=30410951339
smtp_transport_success=true
```

Transport artifact:

```text
artifact_id=8708340165
artifact_digest=sha256:65410e095372a95cab77adbddc727fdd7c28ae49d548db6fc8b3729a78d203c6
```

### Mailbox verification

The same message is present in Sent and Inbox.

Verified MIME inventory:

- Dutch PDF: 142,103 bytes
- English PDF: 138,959 bytes
- Dutch HTML: 115,823 bytes
- English HTML: 112,733 bytes
- inline PNG: 57,780 bytes
- inline-image count: 1
- matching CID reference: 1

Privacy-minimal receipt:

```text
control/evidence/etf_eu_shadow_cid_mailbox_receipt_wp_sync_08_cid_20260729_002500.json
```

No recipient plaintext or raw MIME is stored.

## 5. Blocked activation package

Package:

```text
package_id=ETF-EU-SYNC-CUTOVER-READINESS-20260729
workflow_run_id=30411531406
artifact_id=8708563958
artifact_digest=sha256:cb3880c366a18b066ca8895dbd5da9c213ca580da2121376f59f556b0a4b0ed4
status=blocked_not_activation_ready
activation_ready=false
package_blocker_count=27
```

The package binds:

- immutable donor contract and source commit;
- validated EU design commit;
- exact official portfolio and ledger hashes;
- policy Stage-1 simulation;
- blocked Stage-2 readiness;
- product-evidence gaps;
- verified shadow Gmail receipt;
- state-oriented rollback boundary.

It contains:

```text
authorization_present=false
executable_trade_intents=[]
portfolio_mutation=false
ledger_write=false
funding_authority=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
```

## 6. Official state remains unchanged

```text
portfolio_state=output/etf_eu_portfolio_state.json
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger=output/etf_eu_trade_ledger.csv
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
nav_eur=99756.76
cash_eur=60439.44
position_count=3
ledger_record_count=4
```

Official holdings remain:

- VWCE: 151 shares
- EUNA: 1,526 shares
- SXR8: 10 shares

## 7. Shadow Stage-1 result

The reviewed simulation remains:

- VVSM: 156 simulated shares
- LOCK: 995 simulated shares
- all incumbents retained
- turnover: 24.992241% NAV
- projected cash: €35,483.06 / 35.569579%
- position count: 5

This result is not authorized and has not been applied.

## 8. Stage-2 result

Capacity analysis:

```text
IXUA maximum tranche=15.00% NAV
cash source=10.569579% NAV
SXR8 source=4.430421% NAV
EUNA source=0.00% NAV
projected cash floor=25.00% NAV
```

Stage 2 is blocked by:

- Stage 1 not authorized or applied;
- no official post-Stage-1 state or execution receipt;
- IXUA document, valuation and tradability grades incomplete;
- donor fresh-add direction absent;
- separate Stage-2 authorization absent.

No executable Stage-2 intent exists.

## 9. Exact files added or materially changed in WP-SYNC-08

### Decision and policy

- `config/etf_eu_stage_2_transition_policy_v1.yml`
- `control/ETF_EU_STAGE_2_TRANSITION_AND_ROLLBACK_CONTRACT_V1.md`
- `control/decisions/ETF_EU_SYNC_WP08_CUTOVER_READINESS_DECISION_20260729.md`

### Runtime and validation

- `runtime/build_etf_eu_stage_2_readiness_v2.py`
- `tools/validate_etf_eu_stage_2_readiness.py`
- `runtime/send_etf_eu_shadow_cid_delivery.py`
- `tools/validate_etf_eu_shadow_cid_transport.py`
- `tools/validate_etf_eu_shadow_cid_mailbox_receipt.py`
- `runtime/build_etf_eu_sync_blocked_activation_package.py`
- `tools/validate_etf_eu_sync_blocked_activation_package.py`

### Workflows

- `.github/workflows/validate-etf-eu-transition-replay.yml`
- `.github/workflows/validate-etf-eu-shadow-cid-transport.yml`
- `.github/workflows/send-etf-eu-shadow-cid-delivery.yml`
- `.github/workflows/validate-etf-eu-shadow-cid-live-delivery.yml`
- `.github/workflows/validate-etf-eu-sync-blocked-activation-package.yml`

### Evidence and source locks

- `config/etf_eu_sync_cutover_package_sources_20260729.yml`
- `control/evidence/etf_eu_shadow_cid_mailbox_receipt_wp_sync_08_cid_20260729_002500.json`
- `control/run_queue/etf_eu_shadow_cid_delivery_request_20260729_001500.md`
- `control/run_queue/etf_eu_shadow_cid_delivery_request_20260729_002500.md`

### Operating controls

- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`

## 10. Next safe action

Review PR #66 as a shadow-architecture merge only.

Recommended merge posture:

```text
review all four architecture layers
verify official state hashes
review 27 activation blockers
prefer squash merge
keep PR draft until review is complete
no Stage-1 activation
no Stage-2 activation
no production report replacement
```

After architecture acceptance, create a separate WP-SYNC-09 for fresh Xetra valuation/spread evidence, exact LOCK KID capture and a distinct Stage-1 activation decision.

## 11. Prohibited interpretation

Do not interpret any of the following as portfolio authorization:

- a green CI run;
- the donor target weight;
- the historical composition replay;
- the executive shadow report;
- successful SMTP transport;
- Gmail Sent/Inbox receipt;
- merging PR #66.

Portfolio mutation requires a new accepted package with fresh evidence and explicit authorization.
