# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
FREEZE_REPAIRED_PR91_AND_START_FRESH_INDEPENDENT_ASSURANCE
```

Current authoritative lineage:

```text
parent_work_package=ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1
repair_work_package=ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_V1
active_claim=ETF-EU-DONOR-PARITY-RECONCILIATION-V1
branch=agent/etf-eu-donor-parity-reconciliation-v1
pull_request=91
parent_issue=90
failed_assurance_issue=92
failed_frozen_head=a9f93af018623011ac4b2cae742d69ea1441b4ca
last_green_semantic_head=19954692ff8b33d5ffac9b09d6654210a7194997
target=main
merge_authorized=false
delivery_authorized=false
principal_decision_required=false
principal_action_required=false
```

## Completed repair — do not reopen without regression evidence

### Pricing contract
```text
report_date explicitly bound=true
canonical_pricing_schema=ucits_close_price_validation_basket_results_v2
funded_two_provider_consensus_fail_closed=true
v2_validator_and_normalized_state_same_contract=true
legacy_min_threshold_release_gate=false
report_date_drift_negative_test=true
one_provider_negative_test=true
```

### Markdown/output contract
```text
markdown_state_derived=true
dynamic_funded_count=true
funded_tickers_include_L0CK=true
three_position_copy_fail_closed=true
retired_target_reserve_copy_fail_closed=true
markdown_delivery_validation=true
client_internal_enum_leak_closed=true
```

### End-to-end proof
Semantic head `19954692ff8b33d5ffac9b09d6654210a7194997`:
- donor parity/full six-artifact candidate build run `31433054217` — SUCCESS, 31 tests passed;
- product boundary `31433053898` — SUCCESS;
- release evidence preflight `31433054597` — SUCCESS;
- shadow CID `31433054225` — SUCCESS;
- strategy synchronization shadow `31433054231` — SUCCESS;
- target allocator shadow `31433054316` — SUCCESS;
- transition composition replay `31433054295` — SUCCESS.

## Remaining sequence

1. Finish governance reconciliation of claim/changelog around the completed repair.
2. Write `handover/ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_V1_20260810.md` as the final candidate mutation.
3. Re-read live PR #91 head after that handover commit. That resulting SHA becomes the only frozen fresh-assurance target.
4. Mark PR #91 ready for review without changing its head.
5. Open a **new assurance issue distinct from #92** bound to that exact SHA.
6. Required independent verdict:

`ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS | FAIL | INDETERMINATE`

7. Fresh reviewer must independently re-check:
   - old pricing blocker is closed end to end;
   - old Markdown/L0CK blocker is closed in actual delivery artifacts;
   - full six-artifact package regression is meaningful;
   - four protected funded positions remain unchanged;
   - retired 50/35/15 and research-only 25/18 authority boundaries remain intact;
   - candidate/delivery workflow separation remains intact;
   - no portfolio/ledger mutation, broker execution or send occurred.
8. If PASS and frozen head remains unchanged, merge PR #91.
9. Run exact-main validation and reconcile project + central Control state.
10. Close issue #90 and the integration claim only after exact-main evidence is sufficient.

## Separate post-release production sequence

Only after PR #91 closeout:
1. create a new non-main candidate for the genuinely current Weekly ETF EU report;
2. resolve latest valid completed close;
3. run donor discovery → UCITS mapping → exact-line pricing → current re-underwriting;
4. generate NL/EN MD/HTML/PDF from one state;
5. independently assure the exact report candidate;
6. merge/exact-main validate if PASS;
7. guarded delivery only under separate principal send authority;
8. delivery success only with positive receipt/attachment evidence.

## Decisions not reopened
The assurance FAIL was an implementation/output-contract failure, not an allocation-policy decision. Do not reopen the existing allocation authority without new decision evidence.

## Prohibited shortcuts
Do not:
- merge failed head `a9f93af...`;
- reuse issue #92 for the repaired head;
- mutate the candidate after fresh assurance begins;
- treat CI/machine preflight as independent assurance;
- send email or execute broker actions from this repair mandate.
