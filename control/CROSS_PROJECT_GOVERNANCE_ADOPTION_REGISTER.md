# Cross-Project Governance Adoption Register

## Registry status

```text
registry_date=2026-08-05
canonical_repository_target=market-predictions/control-plane
repository_creation_status=USER_ACTION_REQUIRED
interim_registry_host=market-predictions/weekly-etf-eu
standard=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
reporting_family_bootstrap_rollout=COMPLETE
```

## Adoption portfolio

| Project repository | Risk class | Current status | Current maturity | Target maturity | Evidence / next action |
|---|---|---|---|---|---|
| `market-predictions/weekly-etf-eu` | financial report + delivery | enforced | LEVEL_4 | LEVEL_4 | PR #75 merged as `8f5598176b6a1cc2712159eebd5e14fda7d18706`; keep gate active and complete governed fresh delivery |
| `market-predictions/weekly-etf` | financial report + delivery | documented | LEVEL_1 | LEVEL_4 | PR #114 merged as `e8ad6d31ca0505f3b2ff0b42823fa688a4723a1d`; design ETF-specific assurance contract and hard pre-send gate |
| `market-predictions/weekly-index` | financial report + delivery | documented | LEVEL_1 | LEVEL_4 | PR #2 merged as `8f5546d636052cfa2d912530a6871af06c3a2a82`; design Index-specific assurance and bilingual delivery gate |
| `market-predictions/weekly-fx` | lab financial workflow | documented | LEVEL_1 | LEVEL_3 lab / LEVEL_4 production | PR #1 merged as `74360f0bfaa1ddfbd0f6ea3d2b198a1b16aa2f78`; add lab hard gate, then promote separately to `daily-fx` |
| `market-predictions/daily-etf` | protected production | not yet adopted | LEVEL_0 | LEVEL_4 | assess after Weekly ETF governance contract is validated |
| `market-predictions/daily-index` | protected production | not yet adopted | LEVEL_0 | LEVEL_4 | assess after Weekly Index governance contract is validated |
| `market-predictions/daily-fx` | protected production | not yet adopted | LEVEL_0 | LEVEL_4 | promote only after Weekly FX lab evidence passes |
| `market-predictions/dtr` | strategy research / backtest | candidate | LEVEL_0 | LEVEL_3 | add data-partition, leakage, holdout, execution-assumption, and reproducibility assurance |
| `market-predictions/rendezvue` | privacy/security production app | high-priority candidate | LEVEL_0 | LEVEL_4 | add access-control, revocation, deletion, and deployment assurance |
| SolidPrivacy Scrub repository | privacy-sensitive document app | high-priority candidate | LEVEL_0 | LEVEL_4 | add local-processing, masking, reversibility, and document-integrity assurance; repository access required |

## Central control-plane backlog

### CP-01 — Create repository

```text
repository=market-predictions/control-plane
visibility=recommended_private
owner=USER
status=BLOCKED_BY_REPOSITORY_CREATION
```

The connected GitHub interface can edit existing repositories but cannot create a new repository. The user must create the empty repository once.

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

Replace interim Weekly ETF EU links in Weekly ETF, Weekly Index, and Weekly FX with canonical `market-predictions/control-plane` links.

Owner: assistant after CP-02.

### CP-04 — Add drift audit

Add a periodic or manual audit that checks:

- every registered project has a local governance bootstrap;
- pinned standard versions are current;
- project-specific contracts exist at declared paths;
- production actions have the declared assurance gates;
- stale or broken canonical links are reported.

Owner: assistant.

## User-only actions

1. Create the empty GitHub repository `market-predictions/control-plane`.
2. Replace or upload the revised bootstrap file in each ChatGPT Project when convenient; repository changes cannot modify ChatGPT Project uploads or Project settings.
3. Decide whether the central repository should be private or public. Private is recommended because the register describes internal project topology and controls.
4. Supply access to repositories not visible to the connected GitHub account when their adoption work begins.

## Assistant-owned actions

- seed and maintain the canonical control-plane files after repository creation;
- repoint the already-merged project-local bootstraps;
- create project-specific machine evidence and CI gates;
- verify runs, manifests, receipts, and closeout evidence;
- maintain the adoption register and drift audit;
- report one consolidated status to the user.
