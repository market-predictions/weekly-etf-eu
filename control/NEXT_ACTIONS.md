# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
LAND_GOVERNANCE_GATE_THEN_REPAIR_PR72_AND_RUN_FRESH_END_TO_END_RELEASE
```

The immediate objective is no longer merely to produce another rendered report. The project must first prevent implementation work from certifying its own release readiness, then repair the known validator and workflow defects, and finally execute one fully evidenced report cycle.

## Active governance work package

```text
work_package=ETF_EU_GOV_RA_20260805
implementation_role=implementation_operations
assurance_role=governance_release_assurance
user_interface=single_coordinated_project_stream
portfolio_mutation=false
email_delivery=false
```

## Required release sequence

1. Keep the merged governance release-assurance change active.
2. Rebase or port the governance gate into the fresh-report branch associated with PR #72.
3. Replace the stale production validator assumptions that require exactly three positions and a blocked Stage-1 state.
4. Confirm the selected portfolio mode from authoritative state rather than hard-coded ticker counts.
5. Disable or quarantine the legacy `generate_predictions.yml` FX scheduler as a Weekly ETF EU production path.
6. Generate a new release candidate with current pricing and immutable run identity.
7. Run the independent pre-send governance reconstruction and require `PASS`.
8. Execute guarded transport only after the governance gate passes.
9. Verify transport evidence, attachment hashes and independent inbox receipt.
10. Report `DELIVERY_CONFIRMED` only after the production closeout evidence exists.

## Governance acceptance criteria

The user should continue to issue one project instruction. Internal routing must remain invisible operationally except in the consolidated status. Role A may create `RELEASE_CANDIDATE_READY`; only Role B may issue `GOVERNANCE_PASS_PRE_SEND` or a blocker decision.

## Known defects still requiring implementation repair

- PR #72's final production validator is stale and encodes the previous three-position blocked state.
- The default scheduled `generate_predictions.yml` invokes a legacy FX script and depends on `TWELVEDATA_API_KEY`; it is not a Weekly ETF EU report generator.
- A rendered report has previously been mistaken for a completed delivery even though persistence, send and receipt steps were skipped.
- Repository entry-point documentation was stale and understated the current production architecture.

## Cross-project governance rollout — 2026-08-05

1. Maintain `control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md` as the interim shared standard.
2. Maintain `control/CROSS_PROJECT_GOVERNANCE_ADOPTION_REGISTER.md` as the rollout backlog and status authority.
3. Add thin project-local bootstraps to Weekly ETF, Weekly Index, and Weekly FX.
4. Keep each sibling project at its honest enforcement maturity until its own machine evidence and hard gate exist.
5. User creates the empty repository `market-predictions/control-plane`.
6. Migrate canonical files to the control-plane repository and repoint local bootstraps.
7. Add a cross-project drift audit after migration.

User-only action:

```text
CREATE_EMPTY_REPOSITORY=market-predictions/control-plane
recommended_visibility=private
```

## Prohibited shortcuts

Do not:

- ask the user to coordinate two agents;
- let the implementation role write its own governance `PASS`;
- let governance silently fix and approve the same candidate;
- treat successful pricing, rendering or package validation as delivery proof;
- send artifacts whose hashes are not bound to a governance evidence record;
- claim receipt from SMTP success alone;
- retain legacy workflow names as production authority without explicit system-index registration;
- copy the full cross-project standard into individual operational prompts.
