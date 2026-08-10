# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
FREEZE_AND_INDEPENDENTLY_ASSURE_PR91_DONOR_PARITY_RECONCILIATION
```

Current authoritative work lineage:

```text
work_package=ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1
active_claim=ETF-EU-DONOR-PARITY-RECONCILIATION-V1
branch=agent/etf-eu-donor-parity-reconciliation-v1
pull_request=91
issue=90
target=main
principal_decision_required=false
principal_action_required=false
```

## Remaining sequence

1. Complete the final exact-head PR validation cycle after workflow-authority cleanup. Required gates include:
   - donor-parity and funded-renderer authority regression;
   - product boundary;
   - release-evidence machine preflight contract;
   - the three intentionally retained research-only donor-shadow validations.
2. If any exact-head gate fails, repair on the implementation branch and repeat exact-head validation. Do not hand over a knowingly failing candidate.
3. Write one final implementation handover as the last repository mutation on the candidate line. The handover must identify:
   - PR #91 and current base/main relationship;
   - the last fully validated pre-handover head and its CI runs;
   - completed acceptance criteria;
   - changed-file/workflow-authority scope;
   - explicit protected boundaries;
   - `HANDOVER_READY` disposition;
   - the rule that the independent assurance issue binds the resulting live PR head containing the handover commit.
4. After that handover commit, re-read the live PR head and do not mutate it further. That SHA is the frozen assurance candidate.
5. Open a fresh independent assurance issue bound to that exact SHA. Required verdict:

   `ETF_EU_PR91_DONOR_PARITY_ASSURANCE: PASS | FAIL | INDETERMINATE`

6. Independent assurance must verify at minimum:
   - donor decision/state concepts are present without importing U.S.-specific product assumptions;
   - retired 50/35/15 and historical CAP01 target weights cannot become current controls;
   - donor 3%/5% cash and ~40% factor thresholds are review/disclosure triggers, not allocation caps;
   - four protected funded positions including L0CK are represented consistently;
   - missing current re-underwriting remains unresolved rather than implicit Hold;
   - donor discovery → UCITS mapping → exact-line pricing → fundability → explicit allocation lineage is fail-closed;
   - macro freshness uses donor provenance;
   - twenty historical executable/client-like workflow routes are disabled;
   - the retired allocator sister-report route cannot render a parallel client output from historical policy;
   - candidate workflow cannot self-assure, push candidate output to main or deliver;
   - controlled transport is the sole active real delivery path and is bound to independent PASS plus exact artifact hashes;
   - machine preflight does not claim independent assurance;
   - no portfolio/ledger mutation, broker execution or send occurred on PR #91.
7. If independent assurance is `PASS`, verify the reviewed head is unchanged, then merge PR #91.
8. Run exact-main validation after merge and reconcile:
   - `control/CURRENT_STATE.md`;
   - `control/NEXT_ACTIONS.md`;
   - `control/WORK_CLAIMS.json`;
   - work-package/roadmap/handover records;
   - governance changelog/decision record;
   - central `market-predictions/control-plane` freshness cache/state.
9. Close issue #90 and the integration claim only after the merged lineage and exact-main checks are evidenced.

## Separate post-release production sequence

Only after PR #91 release closeout:

1. create a new non-main candidate branch for the genuinely current Weekly ETF EU report;
2. resolve the latest valid completed close from provider evidence;
3. run broad donor discovery and the UCITS fundability bridge;
4. reprice all protected funded lines using the current two-provider/exact-line rules;
5. perform explicit current re-underwriting for every funded holding and classify material cash;
6. generate NL-primary + EN-companion MD/HTML/PDF from one normalized state;
7. independently assure the exact report candidate;
8. merge/exact-main validate if PASS;
9. create guarded-delivery authority only when a separate principal send authorization exists;
10. claim email success only on positive independent receipt/attachment evidence.

The current donor-parity repair mandate is not itself a guarded-send authorization.

## Completed on PR #91 and not to be reopened without regression evidence

```text
allocation_authority_contract_installed=true
retired_50_35_15_non_executable=true
research_25_18_non_authoritative=true
75pct_pricing_coverage_not_position_cap=true
historical_cap01_targets_current_authority=false
legacy_target_metadata_runtime_sanitized=true
broker_neutral_model_investability=true
recommendation_memory_all_funded_positions=true
missing_reunderwriting_fails_unresolved=true
donor_discovery_ucits_fundability_bridge=true
ucits_registry_identity_only=true
macro_freshness_donor_provenance=true
dynamic_completed_close_resolver=true
funded_renderer_shadow_cap01_overlay_removed=true
funded_renderer_four_position_dynamic=true
candidate_workflow_self_assurance=false
candidate_workflow_delivery=false
candidate_workflow_push_main=false
historical_parallel_workflows_disabled=20
allocator_sister_report_shadow_retired=true
active_research_only_donor_shadow_workflows=3
machine_preflight_is_independent_assurance=false
controlled_transport_only_real_delivery_route=true
controlled_transport_exact_artifact_hash_binding=true
```

## Prohibited shortcuts

Do not:
- interpret historical target metadata as current allocation targets;
- infer Hold from `last_action`, an old purchase or the absence of a new trade;
- turn donor cash/factor review thresholds into sizing caps;
- weaken UCITS/KID/ISIN/exact-line/two-provider pricing requirements;
- allow report text or a historical workflow to mutate protected state;
- allow a historical/shadow allocator to create a parallel client-report authority;
- allow implementation or CI to self-certify independent assurance;
- merge after a semantic head change without fresh assurance;
- send email or claim delivery from candidate generation, machine validation or SMTP success alone;
- imply real broker execution from model-portfolio activity.
