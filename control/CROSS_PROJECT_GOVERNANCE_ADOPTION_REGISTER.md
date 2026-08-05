# Cross-Project Governance Adoption Register

## Registry status

```text
registry_date=2026-08-05
canonical_repository_target=market-predictions/control-plane
repository_creation_status=USER_ACTION_REQUIRED
interim_registry_host=market-predictions/weekly-etf-eu
standard=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
```

## Adoption portfolio

| Project repository | Risk class | Current status | Target maturity | Next action | Owner |
|---|---|---|---|---|---|
| `market-predictions/weekly-etf-eu` | financial report + delivery | implemented | LEVEL_4 | keep gate active; complete governed fresh delivery cycle | assistant |
| `market-predictions/weekly-etf` | financial report + delivery | bootstrap rollout | LEVEL_4 | add local bootstrap, then design ETF-specific assurance evidence and hard pre-send gate | assistant |
| `market-predictions/weekly-index` | financial report + delivery | bootstrap rollout | LEVEL_4 | add local bootstrap; extend bilingual delivery contract with independent assurance | assistant |
| `market-predictions/weekly-fx` | lab financial workflow | bootstrap rollout | LEVEL_3 lab / LEVEL_4 production | add local bootstrap; enforce assurance before any lab send; promote separately to `daily-fx` | assistant + user promotion authority |
| `market-predictions/daily-etf` | protected production | not yet adopted | LEVEL_4 | assess after weekly ETF governance contract is validated | later |
| `market-predictions/daily-index` | protected production | not yet adopted | LEVEL_4 | assess after weekly Index governance contract is validated | later |
| `market-predictions/daily-fx` | protected production | not yet adopted | LEVEL_4 | promote only after weekly-fx lab evidence passes | user + assistant |
| `market-predictions/dtr` | strategy research / backtest | candidate | LEVEL_3 | add data-partition, leakage, holdout and reproducibility assurance contract | later |
| `market-predictions/rendezvue` | privacy/security production app | high-priority candidate | LEVEL_4 | add access-control, revocation, deletion and deployment assurance contract | later |
| SolidPrivacy Scrub repository | privacy-sensitive document app | high-priority candidate | LEVEL_4 | add local-processing, masking, reversibility and document-integrity assurance | later; repository access required |

## Central control-plane backlog

### CP-01 — Create repository

```text
repository=market-predictions/control-plane
visibility=recommended_private_or_internal
owner=USER
status=BLOCKED_BY_REPOSITORY_CREATION
```

The assistant cannot create a new repository through the currently connected GitHub interface. The user must create the empty repository once.

### CP-02 — Seed canonical files

After repository creation, migrate:

- `README.md`
- `control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md`
- `control/CROSS_PROJECT_GOVERNANCE_ADOPTION_REGISTER.md`
- `templates/PROJECT_GOVERNANCE_BOOTSTRAP_TEMPLATE.md`
- `templates/PROJECT_PROMPT_GOVERNANCE_CLAUSE.md`
- `control/DECISION_LOG.md`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`

Owner: assistant after CP-01.

### CP-03 — Repoint project bootstraps

Replace interim Weekly ETF EU links with the canonical `market-predictions/control-plane` links.

Owner: assistant after CP-02.

### CP-04 — Add drift audit

Add a periodic or manual audit that checks:

- every registered project has a local governance bootstrap;
- pinned standard versions are current;
- project-specific contracts exist at the declared paths;
- production actions have the declared assurance gates;
- stale or broken canonical links are reported.

Owner: assistant.

## User-only actions

1. Create the empty GitHub repository `market-predictions/control-plane`.
2. Replace or upload the revised bootstrap file in each ChatGPT Project when convenient; repository changes cannot modify ChatGPT Project uploads or settings.
3. Decide whether the central repository should be private or public. Private is recommended when the adoption register includes internal project topology or operational controls.
4. Supply access to repositories not visible to the connected GitHub account when their adoption work begins.

## Assistant-owned actions

- maintain the canonical standard and adoption register;
- create project-local bootstrap files and decision records;
- update repository control indexes and roadmaps;
- implement project-specific machine evidence and CI gates;
- verify runs, manifests and closeout evidence;
- report one consolidated status to the user.
