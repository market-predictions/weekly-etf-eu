# Weekly ETF EU — Architecture V2 Decision Log Addendum

**Date:** 2026-08-31  
**Status:** CURRENT STABLE DECISIONS  
**Scope:** Product Architecture Revision V2

This addendum supersedes earlier implementation-specific decisions where they conflict with the current architecture. Earlier entries remain historical provenance; they do not regain current authority merely because they are older or more detailed.

## Decision 1 — Thin Current Kernel is the sole semantic execution layer

Current investment/client semantics are implemented under:

```text
runtime/current/
```

Protected persistent state plus current evidence enters the kernel; the kernel produces one frozen review state. Parallel state builders, allocator/shadow executors, semantic patchers and alternative renderers are retired.

## Decision 2 — One frozen review state owns all client semantics

After the per-run review state is frozen:
- NAV may not be recalculated into a different value downstream;
- selected prices may not change;
- funded-position actions may not change;
- allocation semantics may not change;
- comparator results may not change;
- missing evidence may not be manufactured.

A semantic change requires a new review state and therefore a new candidate head/assurance cycle.

## Decision 3 — Rendering is a pure projection

NL/EN Markdown and HTML are deterministic projections from the frozen state. PDF is generated from the exact HTML. Post-render semantic patch/fix/scrub/reconcile chains are retired.

## Decision 4 — Primary exact close may be valuation-grade without a fresh verifier

For an exact canonical UCITS trading line:
- one qualified statically/correctly bound primary provider with the exact requested completed-session close may be valuation-grade;
- an exact same-date correctly bound verifier within tolerance upgrades evidence confidence;
- a stale/missing/unbound verifier does not invalidate a correct exact-date primary;
- accepted same-date disagreement fails closed;
- stale-only pricing, missing exact close, or identity/primary-binding failure fails closed;
- the authoritative selected valuation is the primary close, not a median blend.

This supersedes the earlier universal requirement that every funded line must always have two live same-date providers.

## Decision 5 — Historical target weights are not current allocation authority

Legacy strategic/phase/target weights are historical allocation metadata only unless re-issued by an explicit current allocation decision. Historical report prose or prior recommendation actions never create a current Hold/Add/Reduce decision.

## Decision 6 — VWCE is the stable accountability comparator

The configured VWCE UCITS trading line is the primary opportunity-cost comparator. It is used to calculate comparator return, active return and related accountability evidence.

It is not:
- an allocation target;
- a volatility target;
- a risk-budget target;
- an automatic trade instruction.

The comparator need not be a funded portfolio holding.

## Decision 7 — Current output namespaces are explicit

Latest candidate package:

```text
output/current/
```

Immutable run and evidence copies:

```text
output/history/<report_date>/<run_id>/
output/evidence/<run_id>/
```

New production logic must not write semantically current artifacts into historical current-looking namespaces.

## Decision 8 — Candidate, assurance, integration and delivery are separate authorities

Lifecycle:

```text
candidate build
→ machine validation
→ independent exact-head assurance
→ governed integration
→ exact-main validation
→ separately authorized guarded transport
→ receipt evidence
```

The implementation worker may not self-assure. Machine preflight is not independent assurance. SMTP transport is not delivery confirmation.

## Decision 9 — Guarded delivery binds to the frozen source manifest

Controlled transport must validate:
- exact assured/integrated lineage;
- exact Thin Current Kernel manifest;
- exact client artifact paths;
- exact artifact hashes;
- explicit send authority and confirmations.

Delivery may not re-render or silently substitute files between approval and transport.

## Decision 10 — Runtime and workflow namespaces are allowlisted

Current top-level runtime is limited to:

```text
runtime/__init__.py
runtime/adapt_weekly_etf_macro_for_eu.py
runtime/current/
runtime/send_etf_eu_controlled_report.py
runtime/write_etf_eu_delivery_evidence.py
runtime/check_etf_eu_delivery_receipt.py
```

Current workflow topology is the six-workflow set documented by `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`.

Additional current-looking executors are rejected unless a governed architecture change explicitly expands the boundary and removes the superseded responsibility they replace.

## Decision 11 — Git history is the default provenance for retired executable code

Retired workflows/runtime modules are deleted from current executable namespaces once their responsibility is superseded and no current reference remains. They are not kept beside production code merely as documentation.

Only incident-relevant forensic artifacts explicitly classified under `archive/` may remain outside Git history.

## Decision 12 — Debt retirement is part of Definition of Done

Every architecture slice must identify and remove superseded:
- executors;
- workflows;
- tests;
- current-looking output paths;
- stale authority documentation.

A new path that leaves the old equivalent active is not considered complete unless the parallelism is explicitly intentional and governed.
