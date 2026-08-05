# Weekly ETF EU — Two-Role Governance Model V1

## Decision

The project uses one user-facing instruction stream and one coordinated project backlog, with two internally separated roles:

1. `implementation_operations`
2. `governance_release_assurance`

The user does not need to brief, monitor, or reconcile two separate agents. The project coordinator routes work between the roles and returns one consolidated status.

## Why this exists

The August 2026 incident showed that component success was mistaken for end-to-end delivery success. Pricing, allocation checks and report rendering progressed, while a legacy scheduler and a stale production validator still prevented the requested delivery. The implementation path was effectively assessing its own readiness.

This model removes self-certification from the release process.

## Role A — Implementation and Operations

Owns:

- pricing, allocation and portfolio-state implementation;
- report generation and rendering;
- workflow and runtime changes;
- defect repair;
- package preparation;
- roadmap, work-package and changelog administration.

May produce a `release candidate`.

May not declare production delivery complete and may not write a governance `PASS` decision.

## Role B — Governance and Release Assurance

Owns:

- reconstruction of the release candidate from repository evidence;
- consistency checks across source SHA, run identity, state, manifests, reports and delivery queue;
- artifact-format and hash verification;
- confirmation that visual review and pre-delivery controls passed;
- release decision: `PASS`, `FAIL`, or `INDETERMINATE`;
- post-send verification of transport evidence and independent receipt evidence.

May not modify the release candidate it is certifying. A defect returns to Role A; the corrected candidate receives a new assurance run.

## Coordinator contract

The coordinator is the single interface to the user and must:

1. translate the user request into acceptance criteria;
2. assign implementation work to Role A;
3. hand an immutable candidate to Role B;
4. prevent delivery when Role B does not return `PASS`;
5. report one consolidated status with the exact stopping point;
6. distinguish generated, validated, sent and independently received.

The coordinator may orchestrate both roles in one conversation or project session, but the evidence and decision boundaries remain separate.

## Mandatory release states

Only these states may be reported:

- `IMPLEMENTATION_IN_PROGRESS`
- `RELEASE_CANDIDATE_READY`
- `GOVERNANCE_FAIL`
- `GOVERNANCE_INDETERMINATE`
- `GOVERNANCE_PASS_PRE_SEND`
- `TRANSPORT_SENT_UNVERIFIED`
- `DELIVERY_CONFIRMED`

The words “done”, “sent”, or “delivered” are prohibited before the matching evidence exists.

## Pre-send evidence contract

A governance `PASS` requires all of the following:

- one immutable source commit SHA;
- one run ID, report date and report suffix;
- parseable package, readiness, routine and visual-review artifacts;
- Dutch HTML, Dutch PDF, English HTML and English PDF present and structurally valid;
- SHA-256 hashes for all four client artifacts;
- consistent run identity across authoritative manifests;
- passed visual review with no blockers;
- delivery queue bound to the same run ID and report date;
- implementation and assurance roles explicitly separated.

The machine-readable evidence is validated by:

```text
tools/validate_etf_eu_release_assurance.py
```

## Post-send evidence contract

Pre-send assurance does not prove delivery. After transport, governance must separately verify:

- transport runner result;
- delivery evidence manifest;
- exact attachment hashes matching the pre-send evidence;
- recipient scope matching authorized configuration;
- independent inbox/receipt confirmation;
- production closeout manifest.

Until these checks pass, status remains `TRANSPORT_SENT_UNVERIFIED`.

## Fail-closed rule

Missing, contradictory or stale evidence is a blocker. The governance role must never infer success from a successful upstream step.
