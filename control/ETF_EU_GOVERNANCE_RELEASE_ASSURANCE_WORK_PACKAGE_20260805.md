# Work Package — ETF EU Governance and Release Assurance

```text
work_package_id=ETF_EU_GOV_RA_20260805
owner_role=implementation_operations
review_role=governance_release_assurance
status=IMPLEMENTED_ON_BRANCH_PENDING_CI
branch=agent/governance-release-assurance
```

## Objective

Prevent Weekly ETF EU implementation work from certifying its own production readiness and give the user one coordinated project interface rather than two separately managed agents.

## Scope

### GOV-01 — Operating model

- Define the two internal roles and their boundaries.
- Define the coordinator as the single user interface.
- Define permitted project status labels.

### GOV-02 — Machine evidence

- Build a run-scoped release-assurance evidence artifact.
- Bind it to source SHA, run ID, report date and report suffix.
- Hash all Dutch and English HTML/PDF artifacts.

### GOV-03 — Independent validation

- Validate role separation.
- Validate required control checks and artifact hashes.
- Reject `FAIL`, blockers, incomplete identity or self-certification.

### GOV-04 — CI enforcement

- Add a dedicated GitHub Actions governance workflow.
- Run positive and negative contract tests.
- Insert the governance gate before guarded send in the canonical routine workflow.

### GOV-05 — Administration

- Register the governance contract in the system index.
- Correct the repository README’s stale operating description.
- Update next actions and changelog.

## Acceptance criteria

- The user supplies one project instruction, not separate agent prompts.
- The implementation role can only create a release candidate.
- The governance role emits a separate machine-readable decision.
- The canonical send path cannot execute unless governance validation returns `PASS`.
- A deliberately failed fixture is rejected by CI.
- No portfolio mutation or email delivery is performed by this work package.

## Out of scope

- Repairing the stale four-position production validator in PR #72.
- Sending the fresh Weekly ETF EU report.
- Confirming inbox receipt.

Those are subsequent implementation and governance cycles after this control layer is merged or rebased into the release branch.
