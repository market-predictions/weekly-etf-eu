# Weekly ETF EU Review OS — Current State

## Authority notice

This file is **NARRATIVE_LIGHT** stable context. It is not a runtime routing table and deliberately does not carry a manually synchronized current `main` SHA, issue number, PR number, claim owner, candidate head or CI result.

Resolve volatile operational state live in this order:

1. canonical `market-predictions/control-plane` queue/claim evidence where available;
2. target repository live `main`, branch, PR/issue and workflow/check evidence;
3. exact candidate/handover/result references;
4. authoritative machine state/output evidence.

If this narrative conflicts with later merged code or protected machine state, live authoritative evidence wins.

## Stable product architecture

Weekly ETF EU uses the Thin Current Kernel defined by:
- `docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md`;
- `docs/runbooks/WEEKLY_ETF_EU_REALIZATION_RUNBOOK_V1.md`.

The product is one weekly EU-investable capital decision plus accountable evidence, communicated through one premium NL/EN report family.

The semantic execution boundary is deliberately small:

```text
protected persistent state + current evidence
→ runtime/current/
→ one frozen review_state
→ pure NL/EN Markdown/HTML
→ PDF from exact HTML
→ exact artifact manifest
```

After freeze, downstream validation/render/delivery may not mutate NAV, selected prices, funded-position actions, allocation semantics, comparator performance or evidence status.

## Canonical runtime topology

Allowed top-level runtime namespace:

```text
runtime/__init__.py
runtime/adapt_weekly_etf_macro_for_eu.py
runtime/current/
runtime/send_etf_eu_controlled_report.py
runtime/write_etf_eu_delivery_evidence.py
runtime/check_etf_eu_delivery_receipt.py
```

Additional top-level runtime executors or subdirectories are forbidden by current reachability validation. Retired builders, allocator/shadow paths, post-render semantic patchers and alternate senders are Git-history provenance, not current execution authority.

## Stable production pricing semantics

`control/PRICING_AUTHORITY_CURRENT.md` is the canonical human-readable policy summary.

- exact source-independent UCITS trading-line identity is mandatory;
- one qualified correctly bound primary provider with the exact requested completed-session close is sufficient for valuation-grade `fresh_exact_unverified` pricing;
- an exact same-date correctly bound verifier within tolerance upgrades confidence to `fresh_exact_verified`;
- stale/missing/unbound verifier evidence does not invalidate a valid exact primary;
- accepted exact same-date disagreement outside tolerance fails closed;
- stale-only/no-exact-close/primary identity or binding failure remains blocked;
- selected valuation price is the authoritative primary close.

The prior universal two-live-provider gate is retired. Historical prose or compatibility names containing `consensus` do not override this policy.

## Stable state topology

Persistent domain truth:
- protected portfolio state;
- authoritative trade ledger;
- dated accountability/valuation history;
- recommendation/re-underwriting memory;
- UCITS identity registry.

Per-run truth:
- one immutable/frozen review state derived from persistent state plus current evidence;
- this is the single semantic source for NL/EN Markdown/HTML/PDF after freeze.

Current candidate package namespace:

```text
output/current/
```

Immutable run/evidence namespaces:

```text
output/history/<report_date>/<run_id>/
output/evidence/<run_id>/
```

Client text never creates portfolio authority. Historical target weights, prior report prose and prior recommendation wording are continuity evidence only.

## Accountability comparator

The stable primary opportunity-cost comparator is the configured VWCE UCITS trading line. Comparator performance is accountability evidence, not an allocation target, volatility target or automatic trading instruction.

## Stable operating boundaries

- no real broker execution;
- no protected share/cash/ledger mutation without explicit current allocation authority;
- no diagnostic-only source promotion merely to force coverage;
- no hard ticker-count target;
- pricing confidence is not an allocation rule;
- candidate generation has no SMTP/delivery authority;
- independent assurance is exact-head and separate from implementation;
- guarded transport sends exact approved artifacts only and may not re-render;
- no delivery-success claim without positive receipt/manifest evidence.

## Stable workflow topology

`control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md` defines the six current/current-supporting workflows:
- candidate build;
- guarded delivery;
- current-kernel regression;
- provider-engine regression;
- release-evidence preflight;
- repository/product-boundary validation.

No historical workflow or runtime path gains authority from remaining in Git history or archive.

## How to answer “what is the current status?”

Do not quote this file as a lifecycle snapshot. Re-read live Control and target-repository evidence, then report observed SHAs/PRs/issues/checks and timestamps. Do not write volatile lifecycle facts back here unless stable topology or authority policy itself changed.
