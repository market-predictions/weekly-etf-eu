# Weekly ETF EU — PR #91 to Post-Merge US Donor Leak Repair Handover

Date: 2026-08-10
Repository: `market-predictions/weekly-etf-eu`
Parent issue: #90
Source PR: #91
Source claim: `ETF-EU-DONOR-PARITY-RECONCILIATION-V1`
Successor issue: #94
Successor PR: #95
Successor claim: `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`
From role: `implementation_operations`
To role: `implementation_operations`
Disposition: `SUPERSEDE`

## Source release outcome
PR #91 frozen head `686c658c03d5ba4cbd208e254822a73b3fb514f2` received independent:

`ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS`

in issue #93, comment `5246389680`, and was merged unchanged as:

`202b0a629af34c697c7b7cb8fdce97fbb56bddbc`

That PASS remains valid for what it reviewed. It does not cover later post-merge bot output or a successor repair candidate.

## Post-merge invalidation event
The automatic main workflow `Persist ETF pricing audit` executed legacy donor path:

`python -m pricing.run_pricing_pass`

and committed:

`d771bde734ffda6120a77b1f4fe0e99bd198cc96`

on top of the merge.

The bot commit added only:
- `output/pricing/price_audit_2026-08-10_20260810_214841.json`;
- `output/pricing/price_cache_2026-08-10.json`.

Those artifacts contain US Weekly ETF holdings/data including GLD, GSG, PAVE, PPA, SMH, SPY and URNM, not the protected ETF EU funded set VWCE/EUNA/SXR8/L0CK.

A second active workflow, `validate-etf-runtime.yml`, also executed the same US donor pricing path and legacy `send_report.py` renderer. It completed green, demonstrating that green status was not equivalent to correct ETF EU product identity.

## Root cause
`pricing/run_pricing_pass.py` is retained donor/US runtime code. Its defaults and semantics include:
- `output/etf_portfolio_state.json`;
- `weekly_analysis_pro_*.md`;
- U.S. close cutoff logic;
- donor shortlist/report parsing.

The defect was not that historical donor code existed; the defect was that active ETF EU workflows still invoked it. The pre-existing repository product-boundary validator checked FX leakage but not US Weekly ETF donor-runtime leakage.

## Successor scope
Issue #94 / PR #95 owns the minimum release repair:
1. retire the two donor execution workflows as `.yml.disabled` audit history;
2. remove the two leaked US pricing artifacts from the repaired candidate;
3. make active-workflow product-boundary and workflow-authority validation fail closed on donor-only execution tokens;
4. add regression tests;
5. reconcile project/Control lifecycle;
6. require fresh exact-head independent assurance before successor merge;
7. require exact-main validation after successor merge.

## Protected boundaries
```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
allocation_decision_reopened=false
```

No protected portfolio shares/cash or trade ledger were changed by the post-merge bot commit or by this handover.

## Next action
Continue only on `agent/etf-eu-post-merge-us-donor-leak-repair-v1`. The old PR #91 claim is terminal as `SUPERSEDED`; PR #91 and issue #93 remain historical release/assurance evidence. Freeze PR #95 only after exact-head tests are green, then route a new independent assurance issue.
