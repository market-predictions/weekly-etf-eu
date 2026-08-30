# Weekly ETF EU Review OS — Current State

## Authority notice

This file is **NARRATIVE_LIGHT** stable context. It is not a runtime routing table and deliberately does not carry a manually synchronized current `main` SHA, issue number, PR number, claim owner, candidate head or CI result.

For volatile operational state, resolve live evidence in this order:

1. canonical `market-predictions/control-plane` queue/claim state;
2. target repository live `main`, branches, PRs/issues and workflow/check evidence;
3. exact candidate/handover/result references where applicable;
4. authoritative machine state/output evidence.

If this narrative conflicts with later merged code or protected machine state, the live authoritative evidence wins.

## Stable product state

Weekly ETF EU is being converged to the Thin Current Kernel defined by:
- `docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md`
- `docs/runbooks/WEEKLY_ETF_EU_REALIZATION_RUNBOOK_V1.md`

The product target is one weekly EU-investable capital decision plus accountable evidence, communicated through one premium NL/EN report family.

## Stable production pricing semantics

`control/PRICING_AUTHORITY_CURRENT.md` is the canonical human-readable policy summary. Stable semantics:

- source-independent UCITS trading-line identity first;
- one qualified correctly bound primary provider with the exact requested completed-session close is sufficient for valuation-grade `fresh_exact_unverified` pricing;
- an exact same-date correctly bound verifier within tolerance upgrades confidence to `fresh_exact_verified`;
- stale/missing/unbound verifier evidence does not invalidate a valid exact primary;
- accepted exact same-date disagreement outside tolerance fails closed;
- stale-only/no-exact-close/primary identity or binding failure remains blocked;
- selected valuation price is the primary close.

The prior universal two-live-provider gate is retired. Compatibility names containing `consensus` are not authority and must have a bounded sunset.

## Stable state topology

Persistent domain truth:
- protected portfolio state;
- authoritative trade ledger;
- dated valuation/accountability history;
- recommendation/re-underwriting memory;
- UCITS identity registry.

Per-run truth:
- one immutable/frozen `review_state_<run_id>.json` derived from persistent state and current evidence;
- this becomes the single semantic source for NL/EN Markdown/HTML/PDF after freeze.

Client text never creates portfolio authority. Prior reports are historical evidence only.

## Stable operating boundaries

- no real broker execution;
- no portfolio/share/cash mutation without explicit current allocation authority;
- no diagnostic-only source promotion merely to force coverage;
- no hard ticker-count target;
- pricing confidence is not an allocation rule;
- candidate generation has no SMTP/delivery authority;
- independent assurance is exact-head and separate from implementation;
- guarded transport sends exact approved artifacts only;
- no delivery-success claim without positive receipt/manifest evidence.

## Stable current-entrypoint contract

Until a later governed revision changes it, the current production workflow entrypoints are indexed by `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`:
- candidate: `.github/workflows/run-weekly-etf-eu-routine.yml`;
- guarded delivery: `.github/workflows/send-weekly-etf-eu-controlled-transport.yml`.

Historical executors must leave current executable/read-first namespaces as they are superseded.

## How to answer “what is the current status?”

Do not quote this file as a lifecycle snapshot. Re-read live Control and target-repository evidence, then report the observed state with exact SHAs/PRs/issues/checks and timestamp as evidence. Do not write those volatile facts back here unless the stable topology or authority policy itself changed.
