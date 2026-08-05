# Decision — Adopt Cross-Project Two-Role Governance Standard

## Date

2026-08-05

## Decision

Adopt `CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1` as the shared governance model for consequential project work.

Use one user-facing coordinator with internally separated roles:

```text
implementation_operations
governance_release_assurance
```

Implementation produces the candidate. Governance independently reconstructs and certifies or rejects it. The user does not separately coordinate the roles.

## Authority model

- Shared principles and status semantics belong in one canonical control-plane standard.
- Project repositories contain thin local bootstrap files and domain-specific assurance contracts.
- Task prompts invoke the standard with a short clause and do not duplicate the full contract.
- Project-specific production authority remains local to each repository.

## Interim hosting decision

Until `market-predictions/control-plane` exists, `market-predictions/weekly-etf-eu` temporarily hosts the canonical standard and adoption register.

This interim hosting does not make ETF EU project-specific rules authoritative for other projects.

## Consequences

- Production readiness cannot be self-certified by implementation.
- A reviewer cannot silently fix and approve the same candidate.
- Action execution and confirmed outcome remain separate states.
- Missing or contradictory evidence produces `FAIL` or `INDETERMINATE`.
- The adoption register becomes the rollout backlog and status authority.

## User action required

Create the empty repository:

```text
market-predictions/control-plane
```

After creation, the assistant will migrate canonical files and repoint project-local bootstraps.
