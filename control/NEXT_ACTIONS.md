# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
REPAIR_PR91_AFTER_INDEPENDENT_ASSURANCE_FAIL
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
target=main
merge_authorized=false
delivery_authorized=false
principal_decision_required=false
principal_action_required=false
```

## Direct P1 actions

### 1. Close pricing-contract blocker

Implement and prove one canonical v2 chain:

```text
candidate request report_date
→ provider qualification
→ ucits_close_price_validation_basket_results_v2
→ funded two-provider consensus gate
→ v2 validator
→ v2 normalized state
→ candidate package
```

Required proof:
- candidate workflow passes `--report-date "$ETF_EU_REPORT_DATE"`;
- candidate workflow passes `--require-funded-consensus`;
- validator binds to `--expected-report-date "$ETF_EU_REPORT_DATE"`;
- protected funded positions must all have qualifying two-provider evidence;
- v1 schema/report-date drift/one-provider evidence/failed gate are negative regressions;
- canonical package imports the v2 normalized-state builder.

### 2. Close Markdown delivery blocker

Make both client Markdown artifacts state-derived.

Required proof:
- dynamic funded count;
- exact protected funded ticker set including L0CK;
- no VWCE/EUNA/SXR8-only hard-coded current-position surface;
- three-position wording fails closed;
- retired strategic/phase target and fixed 7.50% reserve wording fails closed;
- Markdown validation is executed in the canonical candidate machine gate and persisted with candidate evidence.

### 3. Run executable end-to-end candidate regression

Do not rely only on static source assertions or isolated unit tests.

The repaired semantic head must produce executable evidence that crosses the candidate pricing/normalized-state/Markdown contract end to end and demonstrates that the two failed defect classes can no longer pass silently.

Also require all normal PR #91 gates to be green.

### 4. Freeze a new candidate

After the final semantic implementation head is green:
1. update roadmap/work package/changelog/claim to reflect completed repair;
2. write a new repair implementation handover as the final candidate mutation;
3. re-read the resulting live PR #91 head;
4. mark PR #91 ready for review;
5. do not mutate the frozen head afterwards.

### 5. Fresh independent assurance

Open a **new assurance issue** distinct from #92 and bind it to the new exact frozen SHA.

Required verdict:

`ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS | FAIL | INDETERMINATE`

The reviewer must explicitly re-check the two former blockers plus the previously passed authority/product/workflow boundaries. Issue #92 remains historical evidence for the failed head and must not be overwritten as if it covered the repair.

### 6. Merge/closeout only after PASS

If and only if the fresh reviewer returns PASS and the head is unchanged:
1. merge PR #91;
2. run exact-main validation;
3. reconcile `CURRENT_STATE`, `NEXT_ACTIONS`, `WORK_CLAIMS`, roadmap, work package, handover and governance changelog;
4. reconcile central `market-predictions/control-plane` freshness state;
5. close parent issue #90 and the integration claim only with sufficient exact-main evidence.

## Separate post-release production sequence

Only after PR #91 repair closeout:
1. create a new non-main candidate for the genuinely current Weekly ETF EU report;
2. resolve latest valid completed close from provider evidence;
3. run donor discovery → UCITS mapping → exact-line pricing → re-underwriting;
4. generate NL-primary + EN-companion MD/HTML/PDF from one state;
5. independently assure the exact report candidate;
6. merge/exact-main validate if PASS;
7. create guarded delivery authority only under a separate principal send authorization;
8. claim delivery only on positive receipt/attachment evidence.

## Decisions not reopened

Do not reopen without new decision evidence:
- retired 50% maximum position;
- retired 35% minimum cash;
- retired 15% maximum new ETF;
- 75% as position cap;
- 25% turnover / 18% semis as current controls;
- donor cash/factor review thresholds as allocation caps.

The assurance FAIL was an implementation/output-contract failure, not a new allocation-policy decision.

## Prohibited shortcuts

Do not:
- merge the failed head `a9f93af...`;
- treat green component CI from the failed head as release evidence for the repaired head;
- add a compatibility schema string without making the execution chain coherent;
- allow Markdown to remain a lower-grade/unvalidated delivery surface;
- mutate protected portfolio or ledger during this repair;
- send email or execute broker actions from this repair mandate;
- reuse issue #92 as assurance for a new semantic head.
