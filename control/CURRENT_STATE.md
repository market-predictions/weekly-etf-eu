# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-10
repository=market-predictions/weekly-etf-eu
main_sha_at_reconciliation=d771bde734ffda6120a77b1f4fe0e99bd198cc96
state=POST_MERGE_US_DONOR_LEAK_REPAIR_HANDOVER_READY
parent_issue=90
repair_issue=94
pull_request=95
branch=agent/etf-eu-post-merge-us-donor-leak-repair-v1
active_claim=ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1
semantic_baseline=d9b5731bbd0b125e2df9b778282116f9d8c32314
merge_authorized=false
delivery_authorized=false
principal_decision_required=false
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
```

## Prior valid release event
PR #91 frozen head `686c658c03d5ba4cbd208e254822a73b3fb514f2` received independent `PASS` in issue #93 and was merged unchanged as `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`.

That PASS remains valid for PR #91. It does not transfer to later bot output or to PR #95.

## Post-merge defect that prevented closeout
A still-active legacy workflow `Persist ETF pricing audit` executed retained US Weekly ETF runtime `pricing.run_pricing_pass` after the PR #91 merge and committed `d771bde734ffda6120a77b1f4fe0e99bd198cc96` to ETF EU `main`.

That bot commit added exactly:
- `output/pricing/price_audit_2026-08-10_20260810_214841.json`;
- `output/pricing/price_cache_2026-08-10.json`.

The audit contained US Weekly ETF holdings such as GLD, GSG, PAVE, PPA, SMH, SPY and URNM rather than the protected ETF EU funded set VWCE/EUNA/SXR8/L0CK.

The post-merge audit also exposed two further active donor/report paths:
- `validate-etf-runtime.yml` executed `pricing.run_pricing_pass` plus legacy `send_report.py` rendering;
- `validate-etf-lane-breadth.yml` validated donor `weekly_analysis_pro_*` report files instead of the current ETF EU discovery/fundability architecture.

## Repair implemented on PR #95
- `persist-etf-pricing-audit.yml` → `.yml.disabled`;
- `validate-etf-runtime.yml` → `.yml.disabled`;
- `validate-etf-lane-breadth.yml` → `.yml.disabled`;
- both leaked US pricing artifacts deleted from the repair candidate;
- repository-boundary validation upgraded from FX-only protection to active FX + US Weekly ETF donor-runtime protection;
- workflow-authority validation scans active `.yml` and `.yaml` files, requires disabled audit copies for all retired routes, and blocks donor execution/report tokens;
- planted negative tests prove active donor pricing/report invocation fails while `.yml.disabled` audit history remains allowed.

Current topology evidence on semantic baseline `d9b5731...`:

```text
product_boundary_run=31436751783 SUCCESS
donor_parity_run=31436751773 SUCCESS
full_package_regressions=31 passed
active_workflows=32
retired_disabled=23
candidate_route=1
delivery_route=1
us_donor_execution_routes=0
```

## Protected portfolio authority — unchanged
`output/etf_eu_portfolio_state.json`

- VWCE — 151 shares
- EUNA — 1,526 shares
- SXR8 — 10 shares
- L0CK — 934 shares
- cash EUR 50,208.40

The protected portfolio and trade ledger were not modified by the bot leak or by PR #95.

## Allocation authority — not reopened
The post-merge defect is operational/product-boundary only. Existing allocation authority remains unchanged; retired 50%/35%/15% rules and 75% position-cap interpretation remain non-current.

## Release boundary
PR #95 is implementation-converged but not independently assured. The exact assurance identity is the live PR #95 head after the atomic handover commit. Any later head change invalidates a review.

Required next chain:

```text
fresh independent governance_release_assurance on exact PR #95 head
→ PASS + unchanged head
→ merge
→ exact-main product/workflow boundary validation
→ verify no US donor artifact regeneration
→ close issue #94 + parent issue #90 + successor claim
→ reconcile central Control state
```

No report delivery or broker execution is authorized by this repair line.
