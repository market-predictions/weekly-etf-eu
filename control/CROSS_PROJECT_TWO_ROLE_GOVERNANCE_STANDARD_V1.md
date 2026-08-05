# Cross-Project Two-Role Governance Standard V1

## Status

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
version=1.0.0
adopted=2026-08-05
canonical_repository_target=market-predictions/control-plane
interim_canonical_location=market-predictions/weekly-etf-eu/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
```

## Purpose

Prevent implementation work from certifying its own completion while preserving one coordinated user experience.

The user gives one project instruction and receives one consolidated status. Internal separation of duties must not require the user to prompt, monitor, or reconcile two agents.

## Operating model

Every consequential workflow has one coordinator and two internally separated roles:

```text
implementation_operations
governance_release_assurance
```

### Coordinator

The coordinator:

- receives the user's instruction;
- resolves the project and requested outcome;
- routes work between the two roles;
- keeps role boundaries intact;
- reports one consolidated project status;
- owns the verification loop when connected tools expose the evidence.

The coordinator must not convert component success into end-to-end success without the required assurance and closeout evidence.

### Role A — Implementation and Operations

Role A may:

- design and implement changes;
- repair defects;
- prepare state transitions;
- generate reports, builds, deployments, migrations, or release candidates;
- run implementation tests;
- produce implementation evidence.

Role A may issue only implementation statuses, including:

```text
IMPLEMENTATION_IN_PROGRESS
IMPLEMENTATION_BLOCKED
RELEASE_CANDIDATE_READY
```

Role A may not issue governance `PASS`, delivery confirmation, deployment confirmation, migration closeout, or equivalent final assurance conclusions.

### Role B — Governance and Release Assurance

Role B must start from the requested outcome and reconstruct the candidate from authoritative evidence rather than relying on Role A's narrative.

Role B may:

- inspect source identity, manifests, state, logs, tests, hashes, artifacts, receipts, and closeout records;
- compare the candidate against project-specific acceptance criteria;
- identify contradictions, missing evidence, stale assumptions, or unauthorized changes;
- issue one of the allowed assurance decisions.

Role B may not silently modify the candidate it certifies. A candidate requiring modification must return to Role A and undergo a new assurance pass.

Allowed assurance decisions:

```text
PASS
FAIL
INDETERMINATE
```

## Trigger rule

Use the two-role cycle when work is consequential, externally visible, irreversible, financially relevant, privacy-sensitive, security-sensitive, production-facing, or described as ready, complete, delivered, deployed, published, migrated, deleted, or released.

Low-risk exploration, brainstorming, early research, and disposable prototypes may use a lighter review unless the project contract says otherwise.

## Mandatory handoff cycle

```text
user request
→ implementation and operations
→ immutable or identifiable release candidate
→ independent governance and release assurance
→ PASS / FAIL / INDETERMINATE
→ authorized production action
→ post-action verification
→ closeout
```

A failed candidate returns to implementation. The repaired candidate must receive a fresh assurance pass.

## Status contract

Projects should map their workflow to these standard statuses:

```text
IMPLEMENTATION_IN_PROGRESS
IMPLEMENTATION_BLOCKED
RELEASE_CANDIDATE_READY
GOVERNANCE_FAIL
GOVERNANCE_INDETERMINATE
GOVERNANCE_PASS_PRE_ACTION
ACTION_EXECUTED_UNVERIFIED
OUTCOME_CONFIRMED
```

Project-specific aliases are permitted, but they must preserve the distinction between:

- candidate readiness;
- pre-action assurance;
- action execution;
- independently confirmed outcome.

## Evidence contract

Before `GOVERNANCE_PASS_PRE_ACTION`, evidence should identify, where applicable:

- repository and source commit SHA;
- branch or release tag;
- run, build, migration, report, or deployment ID;
- authoritative input/state references;
- expected output contract;
- implementation test results;
- immutable artifact identities or cryptographic hashes;
- authorization scope;
- explicit blockers and exceptions;
- assurance role identity distinct from implementation role.

Before `OUTCOME_CONFIRMED`, evidence should identify, where applicable:

- production action result;
- transport, deployment, migration, deletion, or publication manifest;
- receiving-system or independent verification;
- final artifact/state identity;
- closeout status;
- residual risks and deferred follow-up.

Missing or contradictory evidence produces `FAIL` or `INDETERMINATE`, never an inferred pass.

## Enforcement maturity

Each project records one maturity level:

```text
LEVEL_0_DOCUMENTED
LEVEL_1_CHECKLIST
LEVEL_2_MACHINE_EVIDENCE
LEVEL_3_HARD_CI_GATE
LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
```

- `LEVEL_0_DOCUMENTED`: roles and statuses are written down.
- `LEVEL_1_CHECKLIST`: release criteria are explicit and reviewed.
- `LEVEL_2_MACHINE_EVIDENCE`: the workflow creates a structured assurance record.
- `LEVEL_3_HARD_CI_GATE`: the production action cannot proceed without a valid assurance pass.
- `LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION`: completion requires verification from the receiving or target system.

Projects should adopt the highest level justified by consequence and available tooling.

## Project-local adoption requirements

Each adopting repository should contain a small `control/PROJECT_GOVERNANCE_BOOTSTRAP.md` that records:

```text
standard_id
canonical_standard_location
project_repository
project_risk_class
adoption_status
enforcement_maturity
implementation_role
assurance_role
project_specific_assurance_contract
production_action
post_action_confirmation
```

The local bootstrap must not copy the full standard. It links to the canonical standard and defines only project-specific extensions.

Each project should also record the stable decision in its decision log and list any implementation work in `CURRENT_STATE.md` or `NEXT_ACTIONS.md`.

## Project prompt rule

Task prompts should invoke, not duplicate, this standard:

```text
Apply the project's implementation-versus-release-assurance separation. Treat all generated output as a release candidate until independent assurance passes. Do not let implementation certify its own completion.
```

## Anti-patterns

Prohibited:

- requiring the user to coordinate the two roles;
- allowing the builder to issue its own governance pass;
- allowing the reviewer to silently fix and approve the same candidate;
- treating successful generation, rendering, tests, SMTP acceptance, deployment invocation, or deletion request as confirmed outcome;
- using chat narrative as a substitute for repository evidence;
- copying the full standard into every task prompt;
- claiming completion when a real manifest, receipt, target-state check, or closeout record is required but absent.

## Exceptions

A project may use a lighter review only when:

- the action is reversible and non-production;
- no external party or authoritative state is affected;
- the exception is explicit;
- the project-specific contract does not require a stronger gate.

Emergency bypasses for production actions must be explicitly authorized, logged, scoped, and followed by retrospective assurance. Silence or urgency is not authorization.

## Versioning and authority

The canonical standard is versioned centrally. Project repositories pin or reference a version and record local deviations.

Until `market-predictions/control-plane` exists, the interim canonical copy lives in `market-predictions/weekly-etf-eu`. After migration, project bootstraps must point to the control-plane repository and the interim copy becomes historical provenance.
