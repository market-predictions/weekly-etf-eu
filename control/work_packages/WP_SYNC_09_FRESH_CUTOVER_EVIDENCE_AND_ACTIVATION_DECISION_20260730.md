# WP-SYNC-09 — Fresh cutover evidence and Stage-1 activation decision

**Date opened:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/wp09-fresh-cutover-evidence`  
**Status:** claimed and in progress  
**Claimed by:** ChatGPT autonomous development session

## Objective

Create a fresh, fail-closed evidence and decision package for the two policy-selected Stage-1 candidates:

```text
VVSM — VanEck Semiconductor UCITS ETF — IE00BMC38736 — Xetra EUR
LOCK — iShares Digital Security UCITS ETF — IE00BG0J4C88 — Xetra EUR
```

The package must decide whether Stage 1 can be authorized. It must not mutate the official portfolio or ledger and must not create executable orders unless every evidence and authority gate is separately accepted.

## Four-layer scope

### 1. Decision framework

- refresh donor re-underwriting for the two frozen Stage-1 sleeves;
- preserve the current Stage-1 allowlist;
- require explicit pass/fail treatment for identity, KID, current EUR-line valuation, bid/ask, quote size, liquidity, concentration, turnover and cash controls;
- produce an explicit activation decision of `authorize`, `withhold`, or `blocked`;
- default to `blocked` when any required evidence is missing or non-authoritative.

### 2. Input/state contract

- immutable donor contract `weekly_etf_shared_contract_v1_0_0` remains the strategy baseline;
- current donor re-underwriting is evidence only until normalized and validated;
- official issuer sources are required for product identity and exact KID/PRIIPs artifacts;
- official exchange or an explicitly accepted market-data source is required for exact EUR-line valuation and timestamped bid/ask/size;
- cached 2026-07-24 connectivity evidence is not activation-grade;
- official portfolio and ledger hashes are protected inputs.

### 3. Output contract

Required outputs:

```text
output/cutover/etf_eu_wp09_fresh_product_evidence_<run_id>.json
output/cutover/etf_eu_wp09_stage_1_activation_decision_<run_id>.json
output/cutover/etf_eu_wp09_cutover_readiness_manifest_<run_id>.json
```

Every output must expose:

- source lineage and capture timestamp;
- evidence age and exact trading-line identity;
- pass/fail/blocker status per gate;
- no hidden fallback from missing evidence to cached evidence;
- official-state hashes before and after;
- authority flags;
- explicit `executable_trade_intents=[]` unless separately authorized in a later package.

### 4. Operational runbook

- build a bounded fresh-evidence capture workflow;
- validate evidence schema and source roles;
- rebuild the Stage-1 allocator using only accepted evidence;
- build the activation decision;
- validate protected-state hashes;
- upload evidence and decision artifacts;
- do not deliver a report or send email;
- do not write official state or ledger.

## Required evidence gates

### VVSM

- exact fund and Xetra EUR-line identity;
- exact current issuer KID artifact;
- latest accepted completed EUR Xetra close;
- timestamped bid, ask and quote size;
- accepted liquidity evidence;
- evidence within policy age limits.

### LOCK

- exact fund and Xetra EUR-line identity;
- exact current issuer KID/PRIIPs artifact;
- latest accepted completed EUR Xetra close;
- timestamped bid, ask and quote size;
- accepted liquidity evidence;
- evidence within policy age limits.

## Acceptance contract

```text
fresh_evidence_capture_attempted=true
cached_connectivity_not_promoted=true
exact_line_identity_passed=true
exact_kid_passed_for_each_activation_candidate=true
accepted_current_eur_close_passed_for_each_activation_candidate=true
timestamped_bid_ask_size_passed_for_each_activation_candidate=true
liquidity_policy_passed_for_each_activation_candidate=true
donor_reunderwriting_current=true
allocator_rebuilt_from_accepted_evidence=true
protected_state_unchanged=true
activation_decision_explicit=true
portfolio_mutation=false
ledger_write=false
execution_authority=false
production_delivery_authority=false
```

If any required pass is false:

```text
activation_decision=blocked
stage_1_activation_authorized=false
executable_trade_intents=[]
```

## Prohibited shortcuts

- do not treat Yahoo, Stooq or an undated webpage display as accepted activation valuation;
- do not treat issuer NAV in a different currency as the exact Xetra EUR-line close;
- do not infer bid/ask or quote size from daily OHLCV;
- do not reuse the 2026-07-24 cache as fresh evidence;
- do not authorize Stage 1 from report prose or donor target weights;
- do not update official portfolio state or trade ledger;
- do not send a report or test email.

## Initial next actions

1. Inspect the merged upstream donor and EU evidence implementations.
2. Capture current official issuer KID evidence for LOCK and verify VVSM KID currency/date lineage.
3. Test official Xetra/Börse Frankfurt paths for completed close and timestamped quote evidence.
4. Implement evidence normalization and validators.
5. Build the fail-closed activation decision.
6. Run the workflow and stop at a documented external evidence blocker if official public sources cannot provide the required quote evidence.
