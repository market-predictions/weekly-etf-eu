# Weekly ETF EU Review OS

This repository is the European / Dutch-client UCITS ETF review and controlled-delivery system derived from `market-predictions/weekly-etf`.

It is **not** a mechanical translation of the U.S. ETF model. U.S.-listed ETFs and inherited production artifacts are donor material only unless a current EU control contract explicitly grants authority.

## Canonical start sequence

For architecture, pricing, portfolio, report, workflow, governance or delivery work, read:

1. the canonical operating method in `market-predictions/control-plane`;
2. `control/SYSTEM_INDEX.md`;
3. `control/CURRENT_STATE.md`;
4. `control/NEXT_ACTIONS.md`;
5. the minimum relevant implementation files.

Volatile facts such as current `main`, active PR/issue, candidate SHA, claim owner, CI result and delivery receipt must be resolved live. Narrative files are not routing authority.

## Thin Current Kernel

The current product architecture is defined by:

- `docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md`
- `docs/runbooks/WEEKLY_ETF_EU_REALIZATION_RUNBOOK_V1.md`

The executable semantic kernel is deliberately small:

```text
runtime/current/
```

It derives one frozen per-run `review_state` from protected state plus current evidence. NL/EN Markdown, HTML and PDF are pure projections of that frozen state. Downstream renderers, validators and delivery may not change NAV, prices, actions, allocation semantics, comparator results or evidence status.

Current top-level runtime helpers are limited to:

```text
runtime/adapt_weekly_etf_macro_for_eu.py
runtime/send_etf_eu_controlled_report.py
runtime/write_etf_eu_delivery_evidence.py
runtime/check_etf_eu_delivery_receipt.py
```

`tools/validate_etf_eu_current_reachability.py` fails closed if parallel top-level runtime executors reappear.

## Lifecycle separation

### Candidate generation

```text
.github/workflows/run-weekly-etf-eu-routine.yml
```

This non-`main` route may build and validate a candidate and persist candidate evidence. It has no independent-assurance, merge, delivery, SMTP, broker or implicit portfolio-mutation authority.

### Independent assurance

A separate `governance_release_assurance` worker reviews one exact frozen candidate head. Machine preflight is supporting evidence only and is never independent assurance. Any semantic candidate mutation invalidates the assurance verdict.

### Governed integration

Only an independently passed unchanged candidate may proceed to governed integration. Exact-main validation must then prove that the approved semantic candidate is present without unreviewed drift.

### Guarded delivery

```text
.github/workflows/send-weekly-etf-eu-controlled-transport.yml
```

This is the only real ETF EU transport entrypoint. It is main-only, requires exact guarded-delivery authority, binds to the frozen Thin Current Kernel manifest and exact artifact hashes, does not re-render, and persists transport/receipt evidence separately.

SMTP success is not inbox receipt. Delivery is complete only when the delivery layer produces positive receipt/manifest evidence.

## Current pricing semantics

Canonical policy: `control/PRICING_AUTHORITY_CURRENT.md`.

- exact UCITS trading-line identity is mandatory;
- one qualified correctly bound primary provider with the exact requested completed-session close may be valuation-grade;
- a correctly bound exact same-date verifier within tolerance upgrades confidence;
- a stale/missing verifier does not invalidate a correct exact-date primary close;
- same-date disagreement fails closed;
- stale-only pricing, missing exact close, or identity/binding failure fails closed.

The historical universal two-live-provider requirement is retired.

## Persistent and per-run authority

Persistent authority includes protected portfolio state, trade ledger, accountability/valuation history, recommendation memory and the UCITS symbol registry.

Per-run client semantic authority is the frozen Thin Current Kernel review state. Report prose is never portfolio authority and previous reports are historical context only.

## Workflow topology

`control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md` is the canonical operational index. `.github/workflows/` contains only current/current-supporting workflows. Historical executors belong in explicit forensic archive or Git history, not beside production entrypoints.

## Completion semantics

Keep these states distinct:

```text
candidate built and machine-validated
independent exact-head assurance PASS
approved candidate integrated and exact-main validated
guarded transport completed
independent receipt evidence confirmed
```

Never collapse generation, CI, assurance, SMTP transport and delivery confirmation into one success claim.
