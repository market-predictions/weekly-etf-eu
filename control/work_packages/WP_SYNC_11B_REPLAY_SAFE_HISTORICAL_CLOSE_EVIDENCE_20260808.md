# ETF-EU-WP-SYNC-11B — Replay-safe historical completed-close evidence

## Status

```text
work_package=ETF-EU-WP-SYNC-11B
priority=P1
claimed_by=implementation_operations
claim_date=2026-08-08
status=IMPLEMENTATION_IN_PROGRESS
portfolio_mutation=false
ledger_write=false
email_delivery=false
```

## Why this is the current roadmap priority

WP-SYNC-11A established the two-provider completed-close gate and explicitly allowed historical evidence reuse only when bound to the exact report date, basket ID, provider and symbol with immutable provenance. The current production candidate can obtain the most recent Xetra previous-session close, but that live field rolls forward with the market. It therefore cannot independently replay an older requested report date after multiple sessions have elapsed.

This blocks deterministic regeneration and independent assurance of the 2026-08-05 candidate. Rendering or delivery work must not outrank this defect.

## Decision framework

Pricing lineage does not decide portfolio composition. It decides whether a funded line may be represented as current for the requested completed close.

Rules:

1. Preserve the existing requirement for two independent providers on the same completed-close date.
2. Do not weaken the 1.0% agreement tolerance.
3. Preserve ISIN-first EU line identity.
4. Use date-addressable historical evidence for replay; do not infer an old close from a live `previous close` field after that field has rolled forward.
5. Treat source failure as a blocker, not permission to fabricate or relabel a close.

## Input/state contract

For Xetra lines, add a date-addressable Börse Frankfurt historical-price adapter using:

```text
/v1/data/price_history
```

with exact ISIN, MIC and requested date window. The adapter must select only a row whose returned `date` equals the requested report date and whose `close` is positive.

Yahoo Chart remains the independent date-addressable comparison source. At least one provider in the accepted consensus must continue to satisfy the existing line-identity anchor rules.

Every accepted result records:

- requested report date;
- returned close date;
- selected close;
- provider identity;
- exact query ISIN and MIC;
- retrieval mode;
- observation timestamp;
- immutable run-scoped qualification artifact provenance.

## Output contract

The existing `ucits_price_provider_qualification_v2` artifact remains the compatibility surface. A successful replay for the current funded portfolio must show:

```text
funded_line_count=4
funded_consensus_count=4
funded_identity_anchor_count=4
report_pricing_gate_passed=true
```

No client report is generated or sent by this work package.

## Operational runbook

1. Add a deterministic parser for Börse Frankfurt `price_history` payloads.
2. Add planted tests for exact-date selection, missing-date rejection and non-positive close rejection.
3. Route the current pricing v2 entrypoint through historical Börse Frankfurt evidence first.
4. Keep the live previous-session adapter as bounded same/next-session fallback only; it is not replay authority.
5. Add an isolated CI workflow that:
   - runs deterministic tests;
   - performs a live public-source replay for report date `2026-08-05`;
   - requires 4/4 funded two-provider consensus;
   - persists only sanitized pricing evidence as an Actions artifact.
6. If live replay passes, wire the same adapter into the governed fresh-package workflow.
7. If it fails, classify the exact provider/identity/date failure without weakening the gate.

## Governance / assurance boundary

`implementation_operations` may create the adapter and replay evidence. It may not certify release readiness.

`governance_release_assurance` must later verify that the governed candidate references the exact replay-safe pricing artifact and that report/state values equal its selected closes.

## Acceptance criteria

- deterministic historical parser tests pass;
- stale live previous-close inference is not used as replay authority;
- the live 2026-08-05 replay produces 4/4 funded same-date consensus from two providers;
- no portfolio or ledger mutation occurs;
- no email is sent;
- evidence is run-scoped and immutable;
- the existing two-provider and identity-anchor thresholds are unchanged.
