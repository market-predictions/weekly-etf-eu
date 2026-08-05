# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
COMPLETE_CROSS_PROJECT_GOVERNANCE_BOOTSTRAPS_THEN_REPAIR_PR72_AND_RUN_GOVERNED_RELEASE
```

## Governance rollout sequence

1. Complete and merge the interim cross-project standard and adoption register.
2. Add thin project-local governance bootstraps to:
   - `market-predictions/weekly-etf`
   - `market-predictions/weekly-index`
   - `market-predictions/weekly-fx`
3. Record project-specific risk class, target maturity, production action, and post-action confirmation.
4. Keep the full standard centralized; do not duplicate it into every task prompt.
5. User creates the empty repository `market-predictions/control-plane`.
6. Migrate canonical files to the control-plane repository.
7. Repoint project-local bootstrap links from the interim ETF EU host to the control-plane repository.
8. Add a cross-project adoption drift audit.

## Weekly ETF EU release sequence

After the governance rollout documentation is stable:

1. Rebase or port the governance gate into the fresh-report branch associated with PR #72.
2. Replace stale validator assumptions requiring exactly three positions and a blocked Stage-1 state.
3. Resolve selected portfolio mode from authoritative state rather than hard-coded ticker counts.
4. Disable or quarantine `.github/workflows/generate_predictions.yml` as a Weekly ETF EU production path.
5. Generate a fresh release candidate with current pricing and immutable run identity.
6. Run independent pre-send governance reconstruction and require `PASS`.
7. Execute guarded transport only after governance passes.
8. Verify transport evidence, attachment hashes, independent inbox receipt, and production closeout.
9. Report `OUTCOME_CONFIRMED` only after all required evidence exists.

## Cross-project governance acceptance criteria

- The user gives one instruction and receives one consolidated status.
- Implementation may produce only implementation statuses and a release candidate.
- Governance issues `PASS`, `FAIL`, or `INDETERMINATE` from independent evidence.
- Governance may not silently modify the candidate under review.
- A repaired candidate receives a fresh assurance pass.
- Action execution and independently confirmed outcome remain separate statuses.
- Project-local files link to the canonical standard rather than copying it.

## User-only action

```text
CREATE_EMPTY_REPOSITORY=market-predictions/control-plane
```

Recommended visibility: private, because the adoption register may describe internal project topology and controls.

## Known defects still requiring implementation repair

- PR #72's final production validator is stale and encodes the previous three-position blocked state.
- The default scheduled `generate_predictions.yml` invokes a legacy FX script and depends on `TWELVEDATA_API_KEY`; it is not a Weekly ETF EU report generator.
- A rendered report has previously been mistaken for completed delivery even though persistence, send, and receipt steps were skipped.

## Prohibited shortcuts

Do not:

- ask the user to coordinate two agents;
- let implementation write its own governance `PASS`;
- let governance silently fix and approve the same candidate;
- treat pricing, rendering, tests, SMTP acceptance, or workflow invocation as confirmed outcome;
- copy the full cross-project standard into operational task prompts;
- claim delivery without a real manifest and independent receipt evidence.
