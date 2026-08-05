# Work Package — ETF EU Governance and Release Assurance

```text
work_package_id=ETF_EU_GOV_RA_20260805
owner_role=implementation_operations
review_role=governance_release_assurance
status=MERGED_ACTIVE
pull_request=73
merge_commit=30ae248c9eb61045cec8e963ebb9ac84dbf1e476
ci_run=31011973728
ci_conclusion=success
activated_at_utc=2026-08-05T13:48:42Z
```

## Objective

Prevent Weekly ETF EU implementation work from certifying its own production readiness and give the user one coordinated project interface rather than two separately managed agents.

## Scope delivered

### GOV-01 — Operating model

- Defined the two internal roles and their boundaries.
- Defined the coordinator as the single user interface.
- Defined permitted project status labels.

### GOV-02 — Machine evidence

- Added a run-scoped release-assurance evidence builder.
- Bound evidence to source SHA, run ID, report date and report suffix.
- Added SHA-256 hashes for Dutch and English HTML/PDF artifacts.

### GOV-03 — Independent validation

- Added role-separation validation.
- Added required control checks and artifact-hash validation.
- Added fail-closed rejection of `FAIL`, blockers, incomplete identity and self-certification.

### GOV-04 — CI enforcement

- Added a dedicated GitHub Actions governance workflow.
- Added positive and negative contract tests.
- Inserted the governance gate immediately before guarded send in the canonical routine workflow.
- Added pre-send artifact upload so governance evidence survives a later transport failure.

### GOV-05 — Administration

- Registered the governance contract in the system index.
- Corrected the repository README’s stale operating description.
- Updated next actions and the governance changelog.

## Acceptance evidence

- The user supplies one project instruction, not separate agent prompts.
- The implementation role can only create a release candidate.
- The governance role emits a separate machine-readable decision.
- The canonical send path cannot execute unless governance validation returns `PASS`.
- The deliberately failing fixture was rejected by CI.
- The valid fixture and Python compilation passed in CI run `31011973728`.
- PR #73 was squash-merged into `main` as `30ae248c9eb61045cec8e963ebb9ac84dbf1e476`.
- No portfolio mutation or email delivery was performed by this work package.

## Next governed cycle

1. Rebase or port the governance controls into the fresh-report work from PR #72.
2. Repair the stale portfolio-mode validator.
3. Quarantine the legacy FX scheduler as a Weekly ETF EU entry point.
4. Produce a new immutable release candidate.
5. Require governance `PASS` before send and independent receipt evidence before `DELIVERY_CONFIRMED`.
