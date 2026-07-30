# ETF EU WP-SYNC-09 Stage-1 activation decision

**Date:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Pull request:** #68  
**Decision:** `blocked`  
**Status:** completed; activation not ready

## Decision

Stage 1 must not be activated.

The fresh WP-SYNC-09 capture proves the exact identity and current KID of both frozen candidates, but it does not provide activation-grade market evidence and the current donor review does not provide fresh-add authority.

```text
stage_1_activation_authorized=false
official_state_applied=false
portfolio_mutation=false
ledger_write=false
funding_authority=false
execution_authority=false
production_delivery_authority=false
executable_trade_intents=[]
```

## Decision framework

The decision is fail-closed. Each candidate requires all of the following:

1. exact fund and Xetra EUR-line identity;
2. exact current official issuer KID;
3. accepted current completed Xetra EUR close;
4. timestamped Xetra bid, ask and quote size;
5. accepted liquidity measurement;
6. current donor re-underwriting with genuine fresh-add direction.

A missing gate cannot be replaced by cached connectivity evidence, a different-currency issuer NAV, report prose, daily OHLCV, or a historical donor target.

## Input/state findings

### Exact identity and KID — passed

| Portfolio label | Xetra symbol | ISIN | WKN | Exact identity | Exact current KID |
|---|---|---|---|---|---|
| VVSM | VVSM | IE00BMC38736 | A2QC5J | Pass | Pass — 2026-03-27 |
| LOCK | L0CK | IE00BG0J4C88 | A2JMGE | Pass | Pass — 2026-04-09 |

The `LOCK` portfolio label is explicitly distinguished from the Xetra exchange symbol `L0CK`.

### Activation-grade market evidence — blocked

For both candidates:

- the official completed-close API returned HTTP 200 with an empty JSON object;
- the official history crosscheck returned HTTP 200 with an empty JSON object;
- the timestamped quote request timed out;
- no accepted 20-session liquidity measurement was captured.

The 2026-07-24 connectivity cache was not promoted.

### Current donor authority — blocked

Donor evidence is pinned to:

```text
repository=market-predictions/weekly-etf
commit=52f13e190a9f6b0045df175973fdf8d0f6f5f30d
report_date=2026-07-29
```

The donor continues to hold or monitor the two exposures:

- SMH: `hold_with_override`; smaller / under review;
- CIBR: `hold`; hold / monitor.

Both targets remain present, but neither creates a genuine fresh-add direction.

## Exact blockers

```text
LOCK:accepted_current_eur_completed_close
LOCK:accepted_liquidity_measurement
LOCK:timestamped_bid_ask_quote_size
VVSM:accepted_current_eur_completed_close
VVSM:accepted_liquidity_measurement
VVSM:timestamped_bid_ask_quote_size
donor_fresh_add_direction_absent
```

## Output and operational evidence

```text
workflow_run_id=30501245612
job_id=90741172521
validated_head_sha=da90b3f89db1337c267390cc43f84f5e65d1a043
artifact_id=8743584959
artifact_digest=sha256:48ec8c7fcdddcf016378ba19dc0398dadd4432404ea240618d054117fa09e2fc
fresh_evidence_sha256=6c0b21034bdefce2e402741a747126fa1c5bacf7b424e6e3b26e3548d17db62d
activation_decision_sha256=50b4c3008f9c5678b0a98756b6e7c5ec11a17fbe9fdeb5cb4b854b935519937e
cutover_manifest_sha256=e8d907c5310ceda5f709672220c6390a7ffd3d73de5a8b466253430cc2bd9c1d
```

All capture, evidence, decision, manifest and protected-state validators passed. The workflow completed successfully because `blocked` is the correct and validated decision, not because the activation gates passed.

## Protected official state

```text
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
before_after_hashes_equal=true
```

The official model portfolio remains VWCE 151, EUNA 1,526, SXR8 10 and EUR 60,439.44 cash.

## Stable consequence

The reusable WP-SYNC-09 fail-closed evidence capability may be merged into `main`. That merge must not be interpreted as activation authority.

Do not repeat blind high-frequency probing. Reopen the decision only when at least one material dependency changes:

- an accepted source provides the required Xetra completed close, timestamped bid/ask/size and liquidity evidence for both candidates; or
- the donor emits a genuine fresh-add direction and market evidence is simultaneously complete.
