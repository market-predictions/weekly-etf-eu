# Decision — ETF EU WP-SYNC-10 production engine convergence

**Date:** 2026-08-03  
**Status:** accepted for architecture merge; not delivery-enabled

## Decision

Accept the WP-SYNC-10 production-convergence capability as the preferred client-report engine for the next routine-promotion package.

The accepted architecture:

1. rebuilds current Weekly ETF donor strategy and portfolio-target artifacts from a pinned accepted donor commit;
2. maps the current six promoted exposures to six exact UCITS trading lines;
3. separates current promoted opportunities from frozen Stage-1 review continuity;
4. treats the official EU portfolio and cash as the only current-position authority;
5. renders Dutch-primary and English-companion premium HTML/PDF reports;
6. removes development terminology, raw internal identifiers and stale simulated trades from the client surface;
7. keeps all non-actionable target capacity in cash;
8. proves the official portfolio and trade ledger remain unchanged.

## Stable semantic distinctions

```text
current_promoted_exposures=6
mapped_current_promoted_exposures=6
frozen_stage_1_review_candidates=2
VVSM_currently_promoted=false
L0CK_currently_promoted=true
stage_1_decision=blocked
actionable_new_positions=[]
```

A prior review candidate does not remain a current promoted opportunity merely because its evidence review is still open. Conversely, removal from the current promoted set does not erase the accepted evidence and decision history.

## New UCITS mapping decisions

The current water sleeves remain separate:

- `water_infrastructure` → L&G Clean Water UCITS ETF, ISIN `IE00BK5BC891`, Xetra `XMLC`;
- `water_utilities` → iShares Global Water UCITS ETF, ISIN `IE00B1TXK627`, Xetra `IQQQ`.

These mappings complete current opportunity coverage but do not authorize allocation. Current KID and activation-grade market evidence remain separate gates.

## Output decision

The validated production candidate contains:

```text
languages=nl,en
sections_per_language=19
pages_nl=11
pages_en=11
funded_positions=VWCE,EUNA,SXR8
cash_eur=60439.44
cash_weight_pct=60.59
portfolio_delta=0
executable_trade_intents=[]
```

Full visual review of all 22 pages passed with no blank pages, clipping, overlap or orphaned rows.

## Authority boundary

This decision does not:

- activate VVSM, L0CK, IXUA, XMLC, IQQQ or another candidate;
- mutate the official portfolio or ledger;
- authorize broker execution;
- replace the routine report automatically;
- authorize email delivery;
- convert an analytical allocator weight into an actionable target.

## Evidence

```text
validated_head_sha=0997545ad0cf670d805536414d05abde17ff89f2
workflow_run_id=30810262300
job_id=91675081232
artifact_id=8854509533
artifact_digest=sha256:19a5bfcc2db4f813bebc3588946e4843c587ff17aa021d0150835bde58208d65
```

Evidence receipt:

`control/evidence/etf_eu_wp10_production_convergence_30810262300_1.json`

## Next decision

After merging WP-SYNC-10, create a separate package to integrate the converged engine into the routine production runbook, generate a fresh dated package, validate delivery HTML/PDF parity and perform guarded delivery only after its own authorization and receipt gates.
