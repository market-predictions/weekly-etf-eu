# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
MERGE_WP_SYNC_10_THEN_START_WP_SYNC_11_ROUTINE_PRODUCTION_PROMOTION
```

WP-SYNC-10 is complete, machine-green and visually approved. The next step is to merge the reusable production-convergence capability, then create a separate work package that promotes it into the routine production and delivery path.

## Authoritative official baseline

```text
portfolio_position_count=3
cash_eur=60439.44
cash_weight_pct=60.59
invested_market_value_eur=39317.32
nav_eur=99756.76
portfolio_mutation=false
ledger_write=false
```

| Ticker | Shares | Value | Weight | Current action |
|---|---:|---:|---:|---|
| VWCE | 151 | €24,806.28 | 24.866766% | Hold; no change |
| EUNA | 1,526 | €7,465.04 | 7.483242% | Hold; no add or sale |
| SXR8 | 10 | €7,046.00 | 7.063180% | Hold; no second tranche |

No new allocation is currently actionable. Blocked capacity remains cash.

## Completed WP-SYNC-10 capability

The repository branch now provides:

1. current pinned Weekly ETF donor-state rebuilding;
2. six-of-six exact UCITS mapping for the current promoted set;
3. separate current-opportunity and frozen-review contracts;
4. a normalized production-convergence state;
5. state-driven Dutch-primary and English-companion executive surfaces;
6. exact official-position and cash reconciliation;
7. strict client-language and stale-simulation validators;
8. 11-page NL and 11-page EN premium HTML/PDF output;
9. complete 22-page visual review;
10. before/after protected-state hash proof.

Evidence:

```text
head_sha=0997545ad0cf670d805536414d05abde17ff89f2
production_convergence_run=30810262300
artifact_id=8854509533
artifact_digest=sha256:19a5bfcc2db4f813bebc3588946e4843c587ff17aa021d0150835bde58208d65
visual_review_passed=true
```

## Immediate merge sequence

1. Confirm PR #69 contains no official portfolio, ledger or production-send mutation.
2. Confirm all current workflows for the exact PR head are green.
3. Confirm no unresolved review threads.
4. Mark the PR ready for review.
5. Squash-merge the reusable capability.
6. Correct `control/CURRENT_STATE.md` on `main` from branch context to post-merge context.

## WP-SYNC-11 — routine production promotion and guarded delivery

After the WP-SYNC-10 merge, create and claim:

```text
ETF-EU-WP-SYNC-11_ROUTINE_PRODUCTION_PROMOTION_AND_GUARDED_DELIVERY
```

### Decision framework

- Generate a fresh dated Weekly ETF EU report from the converged engine.
- Deploy positions only where all current evidence and authority gates pass.
- Preserve current official positions and cash when a gate fails.
- Keep portfolio mutation separate from report generation and delivery.

### Input/state contract

- Resolve the latest accepted Weekly ETF donor commit and report date.
- Use the current official EU portfolio and ledger.
- Rebuild current six-of-six UCITS mapping and evidence state.
- Use a fresh run ID, report suffix and immutable manifest lineage.
- Do not reuse prior report prose as current truth.

### Output contract

Required fresh package:

```text
Dutch primary HTML/PDF
English companion HTML/PDF
production convergence state
pricing and mapping evidence
client report validation
visual review evidence
delivery manifest
independent inbox receipt
```

The email body must preserve the premium cockpit and decision surfaces after receiving-client rendering. PDF and receiving-mail HTML must tell the same portfolio/action story.

### Operational runbook

1. integrate the converged path into the routine package builder;
2. generate the fresh package without sending;
3. run complete machine and visual validation;
4. create a guarded current-package send authorization bound to exact files and source SHA;
5. send only the authorized package;
6. perform delayed independent Gmail receipt verification;
7. persist a routine manifest and closeout;
8. never infer receipt from SMTP success alone.

## Activation boundary

Stage-1 activation remains blocked:

```text
VVSM_currently_promoted=false
L0CK_currently_promoted=true
VVSM_actionable_target=0.00%
L0CK_actionable_target=0.00%
stage_1_activation_authorized=false
executable_trade_intents=[]
```

Reopen allocation only when a new dated review establishes all required product, close, bid/ask, quote-size, liquidity and donor fresh-add gates.

## Prohibited shortcuts

Do not:

- mutate the official portfolio or ledger merely to make the report look more deployed;
- show analytical allocator weights as current targets;
- restore VVSM to the current opportunity set without current donor promotion;
- treat mapping completeness as funding authority;
- send the WP-SYNC-10 artifact as if it were a fresh routine package;
- claim delivery without a delivery manifest and independent inbox receipt.
