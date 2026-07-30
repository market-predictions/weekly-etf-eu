# Handover — Weekly ETF EU WP-SYNC-09 fresh cutover evidence

**Date:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/wp09-fresh-cutover-evidence`  
**Pull request:** #68  
**Status:** implementation complete; validated blocked decision

## Current issue

The synchronized EU architecture required a fresh activation-grade decision for the two policy-selected Stage-1 candidates:

- VVSM / IE00BMC38736 / Xetra EUR;
- LOCK portfolio label / L0CK Xetra symbol / IE00BG0J4C88 / Xetra EUR.

The earlier cutover package was blocked by broad evidence gaps and could not distinguish a product-document problem from an exchange-market-data problem.

## Root cause

Three independent authorities had been mixed together:

1. exact product and KID authority;
2. exact current Xetra market evidence;
3. current donor fresh-add authority.

The absence of one authority must not invalidate evidence already established in another, and it must never be silently replaced by cached connectivity or historical strategy context.

## Implemented capability

### Decision framework

- exact identity, current KID, close, bid/ask/size, liquidity and donor fresh-add are separate gates;
- any missing required gate produces `decision=blocked`;
- WP-SYNC-09 cannot directly create activation authority or executable trade intents.

### Input/state contract

- exact official issuer KIDs;
- exact Deutsche Börse Xetra identity pages;
- current donor scorecard pinned to commit `52f13e190a9f6b0045df175973fdf8d0f6f5f30d`;
- official portfolio and ledger as hash-protected inputs;
- cached 2026-07-24 connectivity explicitly non-authoritative.

### Output contract

The workflow creates:

```text
etf_eu_wp09_fresh_product_evidence_<run_id>.json
etf_eu_wp09_stage_1_activation_decision_<run_id>.json
etf_eu_wp09_cutover_readiness_manifest_<run_id>.json
```

All outputs include source lineage, capture timestamps, exact blockers, protected-state hashes, false authority flags and `executable_trade_intents=[]`.

### Operational runbook

- bounded fresh network capture;
- exact identity finalization;
- evidence validation;
- fail-closed decision construction;
- decision and manifest validation;
- before/after protected-state hash comparison;
- artifact upload only;
- no report generation, email, portfolio write or ledger write.

## Final evidence result

```text
candidate_count=2
identity_pass_count=2
kid_pass_count=2
accepted_close_pass_count=0
timestamped_quote_pass_count=0
liquidity_pass_count=0
activation_evidence_pass_count=0
```

### Passed

- VVSM exact identity: pass;
- VVSM exact current official KID dated 2026-03-27: pass;
- LOCK/L0CK exact identity: pass;
- LOCK exact current official KID dated 2026-04-09: pass;
- current donor re-underwriting captured: pass;
- protected official state unchanged: pass.

### Blocked

For both candidates:

- official completed-close endpoint returned HTTP 200 with `{}`;
- official history crosscheck returned HTTP 200 with `{}`;
- timestamped quote endpoint timed out;
- accepted 20-session liquidity evidence was unavailable.

The current donor emits hold/monitor treatment rather than a fresh-add direction.

## Decision

```text
decision=blocked
status=blocked_not_activation_ready
decision_blocker_count=7
stage_1_activation_authorized=false
official_state_applied=false
executable_trade_intents=[]
```

Exact blockers:

```text
LOCK:accepted_current_eur_completed_close
LOCK:accepted_liquidity_measurement
LOCK:timestamped_bid_ask_quote_size
VVSM:accepted_current_eur_completed_close
VVSM:accepted_liquidity_measurement
VVSM:timestamped_bid_ask_quote_size
donor_fresh_add_direction_absent
```

## Validation evidence

```text
workflow_run_id=30501245612
job_id=90741172521
validated_head_sha=da90b3f89db1337c267390cc43f84f5e65d1a043
workflow_conclusion=success
artifact_id=8743584959
artifact_digest=sha256:48ec8c7fcdddcf016378ba19dc0398dadd4432404ea240618d054117fa09e2fc
fresh_evidence_sha256=6c0b21034bdefce2e402741a747126fa1c5bacf7b424e6e3b26e3548d17db62d
activation_decision_sha256=50b4c3008f9c5678b0a98756b6e7c5ec11a17fbe9fdeb5cb4b854b935519937e
cutover_manifest_sha256=e8d907c5310ceda5f709672220c6390a7ffd3d73de5a8b466253430cc2bd9c1d
```

Validators:

```text
fresh_evidence_validation=true
activation_decision_validation=true
cutover_manifest_validation=true
protected_state_comparison=true
```

## Official state preservation

```text
nav_eur=99756.76
cash_eur=60439.44
positions=VWCE 151, EUNA 1526, SXR8 10
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
portfolio_mutation=false
ledger_write=false
```

## Files added or materially changed

```text
config/etf_eu_wp09_fresh_evidence_sources.yml
runtime/build_etf_eu_wp09_fresh_evidence.py
runtime/finalize_etf_eu_wp09_identity_contract.py
runtime/build_etf_eu_wp09_activation_decision.py
tools/validate_etf_eu_wp09_fresh_evidence.py
tools/validate_etf_eu_wp09_activation_decision.py
tools/validate_etf_eu_wp09_cutover_manifest.py
.github/workflows/validate-etf-eu-wp09-fresh-cutover.yml
control/work_packages/WP_SYNC_09_FRESH_CUTOVER_EVIDENCE_AND_ACTIVATION_DECISION_20260730.md
control/evidence/etf_eu_wp09_fresh_cutover_evidence_30501245612_1.json
control/decisions/ETF_EU_WP09_STAGE_1_ACTIVATION_BLOCKED_DECISION_20260730.md
control/handovers/HANDOVER_WEEKLY_ETF_EU_WP09_FRESH_CUTOVER_BLOCKED_20260730.md
```

## Next safe action

Merge PR #68 as reusable fail-closed evidence infrastructure only.

After merge, preserve the official portfolio and do not schedule repeated blind probes. Reopen activation work only when an accepted exact Xetra market-data source becomes available for both candidates and the donor simultaneously supplies a genuine fresh-add direction.
