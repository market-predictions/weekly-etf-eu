# WP-SYNC-09 — Fresh cutover evidence and Stage-1 activation decision

**Date opened:** 2026-07-30  
**Date closed:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/wp09-fresh-cutover-evidence`  
**Pull request:** #68  
**Status:** completed; validated blocked decision  
**Claimed and completed by:** ChatGPT autonomous development session

## Objective

Create a fresh, fail-closed evidence and decision package for the two policy-selected Stage-1 candidates:

```text
VVSM — VanEck Semiconductor UCITS ETF — IE00BMC38736 — Xetra EUR
LOCK portfolio label / L0CK Xetra symbol — iShares Digital Security UCITS ETF — IE00BG0J4C88 — Xetra EUR
```

The package must decide whether Stage 1 can be authorized without mutating the official portfolio or ledger and without creating executable orders.

## Four-layer implementation

### 1. Decision framework

Implemented independent gates for:

- exact product and Xetra EUR-line identity;
- exact current official issuer KID;
- accepted current EUR-line completed close;
- timestamped bid, ask and quote size;
- accepted liquidity measurement;
- current donor re-underwriting and genuine fresh-add direction.

Any missing gate produces `decision=blocked`. WP-SYNC-09 itself cannot create Stage-1 authority.

### 2. Input/state contract

Implemented:

- official issuer product/KID sources;
- exact Deutsche Börse line matching by ISIN, WKN, exchange symbol, Xetra and EUR;
- explicit distinction between portfolio label `LOCK` and Xetra symbol `L0CK`;
- donor evidence pinned to commit `52f13e190a9f6b0045df175973fdf8d0f6f5f30d`;
- cached 2026-07-24 connectivity evidence marked non-authoritative;
- official portfolio and ledger as before/after hash-protected inputs.

### 3. Output contract

Delivered:

```text
output/cutover/etf_eu_wp09_fresh_product_evidence_<run_id>.json
output/cutover/etf_eu_wp09_stage_1_activation_decision_<run_id>.json
output/cutover/etf_eu_wp09_cutover_readiness_manifest_<run_id>.json
```

Each output exposes source lineage, capture timestamp, exact blockers, protected-state hashes, false authority flags and `executable_trade_intents=[]`.

### 4. Operational runbook

Delivered:

- bounded fresh network capture in GitHub Actions;
- exact identity finalization;
- evidence validation;
- fail-closed decision construction;
- decision and manifest validation;
- official-state before/after hash comparison;
- artifact upload only;
- no report generation, email, portfolio write, ledger write or execution.

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

### Passed gates

| Candidate | Exact identity | Exact current KID |
|---|---|---|
| VVSM | Pass | Pass — 2026-03-27 |
| LOCK/L0CK | Pass | Pass — 2026-04-09 |

Current donor evidence was captured successfully for both exposures.

### Blocked gates

For both candidates:

- official completed-close endpoint returned HTTP 200 with an empty JSON object;
- official history crosscheck returned HTTP 200 with an empty JSON object;
- official timestamped quote request timed out;
- no accepted 20-session liquidity measurement was captured.

Current donor treatment remains hold/monitor rather than fresh add.

## Final decision

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

## Acceptance contract result

```text
fresh_evidence_capture_attempted=true
cached_connectivity_not_promoted=true
exact_line_identity_passed=true
exact_kid_passed_for_each_activation_candidate=true
accepted_current_eur_close_passed_for_each_activation_candidate=false
timestamped_bid_ask_size_passed_for_each_activation_candidate=false
liquidity_policy_passed_for_each_activation_candidate=false
donor_reunderwriting_current=true
donor_fresh_add_direction=false
protected_state_unchanged=true
activation_decision_explicit=true
activation_decision=blocked
portfolio_mutation=false
ledger_write=false
execution_authority=false
production_delivery_authority=false
```

The failed activation gates correctly triggered the required blocked state.

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
fresh_evidence_validation=true
activation_decision_validation=true
cutover_manifest_validation=true
protected_state_comparison=true
```

## Protected-state closeout

```text
portfolio_state_sha256_before=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
portfolio_state_sha256_after=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256_before=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
trade_ledger_sha256_after=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
```

## Closeout artifacts

```text
control/evidence/etf_eu_wp09_fresh_cutover_evidence_30501245612_1.json
control/decisions/ETF_EU_WP09_STAGE_1_ACTIVATION_BLOCKED_DECISION_20260730.md
control/handovers/HANDOVER_WEEKLY_ETF_EU_WP09_FRESH_CUTOVER_BLOCKED_20260730.md
```

## Stable conclusion

The WP-SYNC-09 capability is complete and suitable for merge as reusable fail-closed evidence infrastructure. Stage 1 is not authorized.

Do not repeat blind high-frequency endpoint probes. Reopen the activation decision only when an accepted source supplies the missing Xetra close, timestamped quote and liquidity evidence for both candidates and the donor simultaneously emits genuine fresh-add authority.
