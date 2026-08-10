# Weekly ETF EU — Post-Merge US Donor Leak Repair V1 — Implementation Handover

Date: 2026-08-10
Repository: `market-predictions/weekly-etf-eu`
Parent issue: #90
Repair issue: #94
Pull request: #95
Branch: `agent/etf-eu-post-merge-us-donor-leak-repair-v1`
Claim: `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`
From role: `implementation_operations`
To role: `governance_release_assurance`
Disposition: `HANDOVER_READY`

## Assurance target rule
The semantic implementation baseline is:

`d9b5731bbd0b125e2df9b778282116f9d8c32314`

This handover and claim transition are committed atomically after that baseline. Therefore the formal assurance target is **not** the semantic baseline SHA. The reviewer must bind the verdict to the live PR #95 head after the atomic handover commit and must verify that head remains unchanged throughout review.

Any subsequent PR-head change invalidates the assurance target and requires a fresh review.

## Why this successor exists
PR #91 was independently assured PASS in issue #93 on exact frozen head:

`686c658c03d5ba4cbd208e254822a73b3fb514f2`

and merged unchanged as:

`202b0a629af34c697c7b7cb8fdce97fbb56bddbc`

After merge, a legacy push workflow executed the retained US Weekly ETF donor runtime and wrote bot commit:

`d771bde734ffda6120a77b1f4fe0e99bd198cc96`

on `main`.

That commit added:
- `output/pricing/price_audit_2026-08-10_20260810_214841.json`;
- `output/pricing/price_cache_2026-08-10.json`.

The pricing audit contained US holdings such as GLD, GSG, PAVE, PPA, SMH, SPY and URNM, not the protected Weekly ETF EU funded set VWCE/EUNA/SXR8/L0CK.

The PASS from issue #93 remains valid for PR #91 but cannot certify later bot output or this successor PR #95.

## Independently reviewable root cause
Three active GitHub Actions routes still carried donor/US output authority:

1. `.github/workflows/persist-etf-pricing-audit.yml`
   - invoked `python -m pricing.run_pricing_pass`;
   - wrote output/pricing JSON back to `main`.
2. `.github/workflows/validate-etf-runtime.yml`
   - invoked `pricing.run_pricing_pass`;
   - invoked legacy `send_report.py` rendering.
3. `.github/workflows/validate-etf-lane-breadth.yml`
   - triggered on donor `output/weekly_analysis_pro_*.md`;
   - invoked donor report-breadth validator `validate_lane_breadth.py`.

`pricing/run_pricing_pass.py` is retained donor code whose defaults/semantics include `output/etf_portfolio_state.json`, `weekly_analysis_pro_*` and U.S. completed-close behavior. Retention is historical/source context; active execution in ETF EU was the defect.

## Implemented repair

### Workflow topology
All three routes above are removed as executable `.yml` workflows and retained only as `.yml.disabled` audit history.

The current workflow-authority gate requires every retired route to have a disabled audit copy and scans both active `.yml` and `.yaml` workflows.

### Product boundary
`tools/validate_etf_eu_repository_boundary.py` now rejects active workflow tokens representing non-EU execution/report authority, including:
- `pricing.run_pricing_pass`;
- `output/etf_portfolio_state.json`;
- `weekly_analysis_pro_`;
- `send_report.py` / `import send_report`;
- `etf.txt`;
- `etf-pro.txt`;
plus the existing FX product-boundary tokens.

Disabled `.yml.disabled` audit history is intentionally not treated as executable.

### Generated artifact cleanup
The two US pricing artifacts introduced by `d771bde...` are deleted from PR #95.

### Preserved donor behavior
The donor breadth concept was not discarded. Current breadth behavior remains represented via the donor discovery → EU research proxy → UCITS mapping → ISIN/KID/exact-line → pricing → re-underwriting → allocation-decision chain. Only the donor report-filename validator was retired.

### Canonical routes unchanged
Candidate/report pricing release authority remains:

`.github/workflows/run-weekly-etf-eu-routine.yml`

Sole real delivery route remains:

`.github/workflows/send-weekly-etf-eu-controlled-transport.yml`

## Semantic evidence
Semantic baseline:

`d9b5731bbd0b125e2df9b778282116f9d8c32314`

### Product boundary
Run `31436751783` — SUCCESS.

Evidence includes:
- 6 planted boundary tests passed;
- full repository active-workflow audit passed;
- no active FX or US Weekly ETF donor execution/report token remained.

### Donor parity / full package
Run `31436751773` — SUCCESS.

Raw job evidence includes:
- 31 package/blocker regressions passed;
- `ETF_EU_WORKFLOW_AUTHORITY=PASS | active_workflows=32 | retired_disabled=23 | candidate_route=1 | delivery_route=1 | us_donor_execution_routes=0`;
- candidate pricing/Markdown wiring PASS;
- static allocation-authority audit PASS.

## Protected state
Protected model portfolio remains:
- VWCE — 151 shares;
- EUNA — 1,526 shares;
- SXR8 — 10 shares;
- L0CK — 934 shares;
- cash EUR 50,208.40.

Protected boundaries:

```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
allocation_decision_reopened=false
```

The post-merge bot incident and PR #95 did not change protected portfolio or ledger authority.

## Required independent review scope
The reviewer must independently establish at minimum:
1. live PR #95 head equals the exact frozen target and does not move during review;
2. the three donor workflows are non-executable and exist only as `.yml.disabled` audit evidence;
3. no other active `.yml/.yaml` workflow contains the prohibited US donor execution/report tokens;
4. the two bot-generated US pricing artifacts are absent from the candidate;
5. canonical candidate and controlled-delivery routes remain intact;
6. issue #93 PASS was not reused as assurance authority for PR #95;
7. protected ETF EU portfolio and ledger are unchanged;
8. raw Actions evidence supports the claimed 31-test/full-package and workflow/product-boundary results;
9. no report delivery, SMTP, portfolio mutation, ledger write or broker execution is authorized by this candidate.

The reviewer must not modify PR #95 or repair defects discovered during assurance.

## Required formal verdict

`ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS | FAIL | INDETERMINATE`

PASS authorizes only the governance-controlled merge step for the exact unchanged reviewed PR #95 head. It does not authorize report generation/delivery, SMTP or broker execution.

## Post-PASS closeout
After PASS + unchanged head:
1. merge PR #95 with exact-head guard;
2. run/inspect exact-main product and workflow boundary validation;
3. prove no US donor pricing artifact is regenerated by push workflows;
4. verify protected EU portfolio/ledger unchanged;
5. close issue #94, parent issue #90 and successor claim only when exact-main evidence is sufficient;
6. reconcile project-local and central Control state.

Delivery remains a separate later authority gate.
