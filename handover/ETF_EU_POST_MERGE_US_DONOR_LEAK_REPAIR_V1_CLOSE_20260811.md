# Weekly ETF EU — Post-Merge US Donor Leak Repair Closeout

Date: 2026-08-11
Repository: `market-predictions/weekly-etf-eu`
Claim: `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`
Parent issue: #90
Repair issue: #94
Assurance issue: #96
Pull request: #95
From role: `implementation_operations`
To role: `portfolio_control / routine operations`
Disposition: `CLOSE`

## Exact lineage

```text
pre-repair main=d771bde734ffda6120a77b1f4fe0e99bd198cc96
reviewed PR95 head=e5d3470e1e1ab7f402a02cb31b775f3f902d4928
assurance verdict=ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS
assurance issue=96
assurance comment=5246954887
merge commit=10823b7c457a253e409a768f52ee95b1522c363f
merge tree=71a614575bdc1d675ece53684d14601ce76fde90
synthetic reviewed merge=d19c7de3c965703de28247fe54dbef05938e80be
synthetic reviewed merge tree=71a614575bdc1d675ece53684d14601ce76fde90
```

The real merge and the synthetic merge used by the frozen PR Actions evidence have the same Git tree. Therefore the independently inspected workflow-authority result on the synthetic merge applies to the exact repository content merged to `main`.

## Scope completed

1. Removed the two erroneous US Weekly ETF pricing artifacts introduced by bot commit `d771bde7...`.
2. Retired the three donor/US operational paths as non-executable `.yml.disabled` audit history:
   - `persist-etf-pricing-audit.yml.disabled`;
   - `validate-etf-runtime.yml.disabled`;
   - `validate-etf-lane-breadth.yml.disabled`.
3. Hardened repository-boundary validation against active FX and US Weekly ETF donor execution/report tokens.
4. Hardened workflow authority across active `.yml` and `.yaml` files and all retired route names.
5. Preserved one canonical candidate route and one guarded delivery route.
6. Preserved donor discovery breadth through the research-only donor-discovery → UCITS mapping/fundability chain rather than donor production/report runtime.

## Independent assurance

Issue #96 returned:

`ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS`

on exact frozen head `e5d3470e1e1ab7f402a02cb31b775f3f902d4928`.

The reviewer independently reconstructed source, active workflow topology, protected state, raw Actions evidence and the prior defect before reading implementation handover material.

## Exact-main verification

Exact code merge SHA:

`10823b7c457a253e409a768f52ee95b1522c363f`

GitHub Actions push run `31472717495` checked out that exact SHA and returned:

```text
Validate Weekly ETF EU product boundary=SUCCESS
planted boundary tests=6 passed
active_workflows_scanned=32
blockers=[]
verdict=PASS
```

The exact-main scan includes prohibited US donor tokens such as `pricing.run_pricing_pass`, `output/etf_portfolio_state.json`, `weekly_analysis_pro_`, `send_report.py`, `etf.txt` and `etf-pro.txt`.

The merge produced exactly one push-triggered Actions run: the product-boundary validator. None of the three retired donor workflows executed again.

Both former leaked artifact paths are absent on exact post-merge `main`:

- `output/pricing/price_audit_2026-08-10_20260810_214841.json` → 404 / absent;
- `output/pricing/price_cache_2026-08-10.json` → 404 / absent.

The frozen PR merge-compatibility workflow-authority evidence was executed on synthetic merge `d19c7de3...` and reported:

```text
active_workflows=32
retired_disabled=23
candidate_route=1
delivery_route=1
us_donor_execution_routes=0
```

Because synthetic merge `d19c7de3...` and real merge `10823b7c...` have the identical tree `71a614575bdc1d675ece53684d14601ce76fde90`, this is exact-content workflow-authority evidence for the merged code tree.

## Protected state verification

Protected portfolio blob on post-merge `main`:

`df710b5fbe4172506b67b7f591030a8c6a098c64`

Protected trade-ledger blob on post-merge `main`:

`c6765ba380fe0c40272688a017dc0dc99b46d571`

These are unchanged from assurance evidence. Funded positions remain VWCE 151, EUNA 1,526, SXR8 10 and L0CK 934; cash remains EUR 50,208.40.

## Protected actions

```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
allocation_decision_reopened=false
```

## Unresolved items

None within the donor-parity / post-merge US donor leak repair scope.

## Next action

The repair/reconciliation line is complete and must not remain as an active claim. Any genuinely current Weekly ETF EU report is a new, separate production candidate cycle using current completed-close EU/UCITS v2 pricing, current re-underwriting, independent report assurance and separately authorized guarded delivery.
