# Work Package — Cross-Project Governance Rollout

```text
work_package_id=CROSS_PROJECT_GOVERNANCE_ROLLOUT_20260805
owner_role=implementation_operations
review_role=governance_release_assurance
status=IN_PROGRESS
interim_host=market-predictions/weekly-etf-eu
canonical_repository_target=market-predictions/control-plane
portfolio_mutation=false
email_delivery=false
```

## Objective

Create one centrally maintained separation-of-duties standard and adopt it through thin project-local bootstraps without requiring the user to manage two agents or duplicate the full governance contract across task prompts.

## Scope

### CP-STD-01 — Canonical standard

- Define coordinator, implementation, and assurance roles.
- Define trigger conditions, statuses, handoff cycle, evidence requirements, and enforcement maturity.
- Preserve one user-facing instruction stream.

### CP-REG-01 — Adoption register

- Register projects, risk classes, adoption status, target maturity, owner, and next action.
- Separate protected production repositories from lab or pilot repositories.

### CP-TPL-01 — Reusable templates

- Add the project governance bootstrap template.
- Add the short task-prompt governance clause.
- Avoid copying the full standard into operational prompts.

### CP-ROLLOUT-01 — Reporting-family adoption

- Weekly ETF EU: register the already enforced LEVEL_4 implementation.
- Weekly ETF: add project-local bootstrap and decision record.
- Weekly Index: add project-local bootstrap and decision record.
- Weekly FX: add lab-aware project-local bootstrap and decision record.

### CP-MIGRATE-01 — Control-plane repository

- User creates `market-predictions/control-plane`.
- Assistant migrates canonical files and repoints local bootstraps.

## Acceptance criteria

- One canonical standard exists.
- One adoption register identifies assistant-owned and user-owned work.
- Project-local files link to the standard rather than copying it.
- The user is not required to coordinate two agents.
- Existing project-specific governance remains authoritative for local evidence.
- No production report, portfolio, email, deployment, or state mutation occurs in this work package.

## Current blocker

```text
blocker=NEW_REPOSITORY_CREATION_NOT_EXPOSED_BY_CONNECTED_GITHUB_INTERFACE
user_action=CREATE_EMPTY_REPOSITORY_market-predictions/control-plane
```

The rollout can proceed using the interim host. Migration to the final control-plane repository requires the one-time repository creation action by the user.
