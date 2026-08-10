# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
CLOSE_POST_MERGE_US_DONOR_EXECUTION_LEAK_ON_PR95
```

Current authoritative lineage:

```text
parent_issue=90
post_merge_repair_issue=94
prior_pr=91
prior_assurance_issue=93
prior_assurance=PASS
prior_reviewed_head=686c658c03d5ba4cbd208e254822a73b3fb514f2
prior_merge_commit=202b0a629af34c697c7b7cb8fdce97fbb56bddbc
post_merge_defect_main=d771bde734ffda6120a77b1f4fe0e99bd198cc96
active_work_package=ETF-EU-WP-POST-MERGE-US-DONOR-LEAK-REPAIR-V1
active_claim=ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1
branch=agent/etf-eu-post-merge-us-donor-leak-repair-v1
pull_request=95
target=main
merge_authorized=false
delivery_authorized=false
principal_decision_required=false
principal_action_required=false
```

## Incident to close

After valid PASS and merge of PR #91, a legacy push workflow executed US Weekly ETF donor runtime and committed US product pricing artifacts to ETF EU `main`.

Bad post-merge bot commit:

`d771bde734ffda6120a77b1f4fe0e99bd198cc96`

Added files:
- `output/pricing/price_audit_2026-08-10_20260810_214841.json`;
- `output/pricing/price_cache_2026-08-10.json`.

The audit contains GLD/GSG/PAVE/PPA/SMH/SPY/URNM. This is not protected ETF EU state and must not survive the repaired release line.

## Implementation sequence — active

1. Keep `.github/workflows/persist-etf-pricing-audit.yml` non-executable as `.yml.disabled` audit history.
2. Keep `.github/workflows/validate-etf-runtime.yml` non-executable as `.yml.disabled` audit history.
3. Keep both erroneous US pricing artifacts deleted from PR #95.
4. Run product-boundary validation across all active `.yml/.yaml` workflows and fail on donor execution tokens including:
   - `pricing.run_pricing_pass`;
   - `output/etf_portfolio_state.json`;
   - `weekly_analysis_pro_`;
   - `send_report.py` / `import send_report`;
   - `etf.txt`;
   - `etf-pro.txt`.
5. Run workflow-authority validation and require the newly retired workflows to have `.disabled` evidence while remaining absent from active workflow names.
6. Inspect CI failures for any additional active US donor route. If found, retire or replace only the affected execution route; do not build a second EU pricing/report authority.
7. Keep the canonical EU candidate route `run-weekly-etf-eu-routine.yml` and controlled transport route unchanged unless a test proves a defect in them.
8. Verify protected `output/etf_eu_portfolio_state.json` and trade ledger remain unchanged.
9. Reconcile roadmap/changelog/workpackage/claim/handover after semantic CI is green.
10. Freeze exact PR #95 head and mark ready for independent review.
11. Open a new assurance issue bound to exact PR #95 head; required verdict:

`ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS | FAIL | INDETERMINATE`

12. Merge only after independent PASS and unchanged head.
13. Exact-main validation must then prove:
   - product-boundary PASS;
   - workflow-authority PASS;
   - no US donor pricing/report workflow has reactivated;
   - no US pricing artifacts are regenerated on main;
   - protected EU portfolio/ledger remain unchanged.
14. Only after that evidence, close issue #94, parent issue #90 and successor claim, and reconcile central Control state.

## Separate post-release production sequence

Only after this architecture/closeout line is complete:
1. create a new non-main candidate for the genuinely current Weekly ETF EU report;
2. resolve latest valid completed close;
3. run donor discovery → UCITS mapping → exact-line two-provider pricing → current re-underwriting;
4. generate NL/EN MD/HTML/PDF from one state;
5. independently assure the exact report candidate;
6. merge/exact-main validate if required by the report release contract;
7. guarded delivery only under separate principal send authority;
8. delivery success only with positive receipt/attachment evidence.

## Decisions not reopened
The post-merge leak is an operational/product-boundary defect. Do not reopen existing allocation authority without new decision evidence.

## Prohibited shortcuts
Do not:
- treat green legacy runtime CI as proof of correct ETF EU product identity;
- preserve the bot-generated US audit/cache as current ETF EU evidence;
- merge PR #95 without fresh exact-head assurance;
- reuse issue #93 PASS as assurance for PR #95;
- send email or execute broker actions from this repair mandate.
