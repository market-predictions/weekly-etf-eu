# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-10
repository=market-predictions/weekly-etf-eu
main_sha_at_reconciliation=d771bde734ffda6120a77b1f4fe0e99bd198cc96
operating_mode=POST_MERGE_US_DONOR_EXECUTION_LEAK_REPAIR
parent_work_package=ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1
active_work_package=ETF-EU-WP-POST-MERGE-US-DONOR-LEAK-REPAIR-V1
active_claim=ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1
working_branch=agent/etf-eu-post-merge-us-donor-leak-repair-v1
pull_request=95
parent_issue=90
repair_issue=94
prior_release_pr=91
prior_assurance_issue=93
prior_assurance_verdict=PASS
prior_reviewed_head=686c658c03d5ba4cbd208e254822a73b3fb514f2
prior_merge_commit=202b0a629af34c697c7b7cb8fdce97fbb56bddbc
state=POST_MERGE_P0_REPAIR_ACTIVE
principal_decision_required=false
principal_action_required=false
merge_authorized=false
delivery_authorized=false
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

## What changed after PR #91 PASS

Independent issue #93 returned:

`ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS`

for exact frozen PR #91 head:

`686c658c03d5ba4cbd208e254822a73b3fb514f2`

The head remained unchanged and PR #91 was merged as:

`202b0a629af34c697c7b7cb8fdce97fbb56bddbc`

That PASS and merge are valid for the reviewed candidate. They did not authorize delivery or broker execution.

## Post-merge P0 defect

Exact-main observation exposed a separate active donor-runtime leak after the merge.

Push workflow `Persist ETF pricing audit` executed retained US Weekly ETF runtime:

`python -m pricing.run_pricing_pass`

and wrote bot commit:

`d771bde734ffda6120a77b1f4fe0e99bd198cc96`

on top of the merge.

The bot commit added exactly two generated files:
- `output/pricing/price_audit_2026-08-10_20260810_214841.json`;
- `output/pricing/price_cache_2026-08-10.json`.

The artifacts contain US Weekly ETF holdings/data including GLD, GSG, PAVE, PPA, SMH, SPY and URNM rather than the protected Weekly ETF EU funded set.

A second active workflow, `Validate ETF runtime changes`, also executed `pricing.run_pricing_pass` and legacy `send_report.py`. It completed green. Therefore the defect is architectural product-boundary leakage, not a failed-job problem.

## Root cause

`pricing/run_pricing_pass.py` is retained donor/US runtime code whose defaults/semantics include:
- `output/etf_portfolio_state.json`;
- `weekly_analysis_pro_*.md`;
- U.S. completed-close timing;
- donor report/watchlist parsing.

Historical donor code may remain for provenance, but active ETF EU workflows may not execute it. The existing product-boundary validator guarded FX leakage but did not guard US Weekly ETF donor-runtime leakage.

## Active repair — issue #94 / PR #95

Successor branch:

`agent/etf-eu-post-merge-us-donor-leak-repair-v1`

Current implemented scope:
- `persist-etf-pricing-audit.yml` retired to `.yml.disabled`;
- `validate-etf-runtime.yml` retired to `.yml.disabled`;
- the two erroneous US pricing artifacts removed from the repair candidate;
- repository-boundary validation now rejects active US donor execution tokens;
- workflow-authority validation now rejects active US donor execution tokens and requires the two newly retired routes to remain disabled;
- planted regressions cover active donor pricing, active legacy renderer and disabled-audit-history behavior.

The previous PR #91 release claim is `SUPERSEDED` after its valid merge because the post-merge defect requires a new exact-head candidate/assurance identity. Successor claim `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1` is the only active release-integration line.

## Protected portfolio authority — unchanged

`output/etf_eu_portfolio_state.json`

| Ticker | ISIN | Venue | Shares |
|---|---|---|---:|
| VWCE | IE00BK5BQT80 | Xetra | 151 |
| EUNA | IE00BDBRDM35 | Xetra | 1,526 |
| SXR8 | IE00B5BMR087 | Xetra | 10 |
| L0CK | IE00BG0J4C88 | Xetra | 934 |

```text
cash_eur=50208.40
funded_position_count=4
model_portfolio_only=true
real_broker_execution=false
```

The erroneous post-merge audit did not mutate this protected state or the trade ledger.

## Allocation authority — NOT REOPENED

`control/ETF_EU_ALLOCATION_AUTHORITY_V1.md` remains canonical.

Retired current authority:
```text
50% maximum position
35% minimum cash
15% maximum new ETF
75% as a position cap
```

Research/shadow only unless separately adopted:
```text
25% turnover
18% AI-compute/semiconductor cap
```

The post-merge defect is an execution/product-boundary defect, not a new portfolio decision.

## Current release boundary

```text
finish PR #95 implementation validation
→ inspect CI for any additional active donor execution route
→ reconcile repair claim/docs
→ freeze exact PR #95 head
→ fresh independent governance_release_assurance
→ merge only after PASS + unchanged head
→ exact-main validation proving no donor artifact regeneration
→ close issue #94 + parent issue #90 + successor claim
→ reconcile central Control state
```

No report email or broker execution is authorized by this repair mandate.
