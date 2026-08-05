# Work Package — Cross-Project Governance Rollout

```text
work_package_id=CROSS_PROJECT_GOVERNANCE_ROLLOUT_20260805
owner_role=implementation_operations
review_role=governance_release_assurance
status=COMPLETE_PENDING_CONTROL_PLANE_REPOSITORY
interim_host=market-predictions/weekly-etf-eu
canonical_repository_target=market-predictions/control-plane
portfolio_mutation=false
email_delivery=false
```

## Objective

Create one centrally maintained separation-of-duties standard and adopt it through thin project-local bootstraps without requiring the user to manage two agents or duplicate the full governance contract across task prompts.

## Completed scope

### CP-STD-01 — Canonical standard

Completed:

- coordinator, implementation, and assurance roles defined;
- trigger conditions, statuses, handoff cycle, evidence requirements, and enforcement maturity defined;
- one user-facing instruction stream preserved.

### CP-REG-01 — Adoption register

Completed:

- projects, risk classes, adoption status, target maturity, owner, and next action registered;
- protected production repositories separated from lab or pilot repositories.

### CP-TPL-01 — Reusable templates

Completed:

- project governance bootstrap template added;
- short task-prompt governance clause added;
- full-standard duplication in operational prompts prohibited.

### CP-ROLLOUT-01 — Reporting-family adoption

Completed:

```text
weekly-etf-eu_pr=75
weekly-etf-eu_merge=8f5598176b6a1cc2712159eebd5e14fda7d18706
weekly-etf_pr=114
weekly-etf_merge=e8ad6d31ca0505f3b2ff0b42823fa688a4723a1d
weekly-index_pr=2
weekly-index_merge=8f5546d636052cfa2d912530a6871af06c3a2a82
weekly-fx_pr=1
weekly-fx_merge=74360f0bfaa1ddfbd0f6ea3d2b198a1b16aa2f78
```

Weekly ETF EU remains honestly recorded at LEVEL_4. Weekly ETF, Weekly Index, and Weekly FX are honestly recorded at LEVEL_1 until their own machine evidence and hard gates are implemented.

## Remaining scope

### CP-MIGRATE-01 — Control-plane repository

Blocked only by one user action:

```text
blocker=NEW_REPOSITORY_CREATION_NOT_EXPOSED_BY_CONNECTED_GITHUB_INTERFACE
user_action=CREATE_EMPTY_REPOSITORY_market-predictions/control-plane
recommended_visibility=private
```

After repository creation, the assistant will:

1. seed the canonical files;
2. migrate the standard and adoption register;
3. repoint project-local bootstraps;
4. add a drift audit;
5. continue project-specific assurance implementation.

## Acceptance criteria status

- One canonical standard exists: **passed**.
- One adoption register exists: **passed**.
- Project-local files link rather than copy: **passed**.
- User does not coordinate two agents: **passed**.
- Project-specific governance remains local: **passed**.
- Reporting-family bootstrap adoption is merged: **passed**.
- No production report, portfolio, email, deployment, or state mutation occurred: **passed**.
- Final control-plane migration: **blocked by user repository creation**.
