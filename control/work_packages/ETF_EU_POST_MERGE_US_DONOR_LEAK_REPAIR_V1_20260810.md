# ETF EU Post-Merge US Donor Leak Repair V1

Date opened: 2026-08-10
Date closed: 2026-08-11
Parent issue: #90
Issue: #94
Pull request: #95
Claim: `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`
Owner role: `implementation_operations`
Status: `CLOSED`

## Trigger
Post-merge validation after independently PASSed PR #91 exposed executable US Weekly ETF donor pricing/report paths inside Weekly ETF EU.

## Root cause
Three active workflows were still coupled to donor/US output/runtime conventions:
1. `.github/workflows/persist-etf-pricing-audit.yml` executed `pricing.run_pricing_pass` and wrote donor pricing state to `main`;
2. `.github/workflows/validate-etf-runtime.yml` executed the same donor pricing runtime and legacy `send_report.py` renderer;
3. `.github/workflows/validate-etf-lane-breadth.yml` validated donor `weekly_analysis_pro_*` report files instead of the ETF EU discovery/fundability architecture.

## Repair completed
- all three legacy donor routes retained only as `.yml.disabled` audit history;
- both leaked US pricing artifacts removed;
- active workflow product-boundary gate blocks FX and US donor execution/report tokens;
- workflow-authority gate scans `.yml` + `.yaml`, requires 23 retired-disabled routes and rejects active donor execution/report tokens;
- canonical EU candidate remains non-main and UCITS-v2/funded-consensus based;
- controlled transport remains the sole real delivery route;
- protected portfolio, ledger and allocation authority unchanged.

## Independent assurance

Issue #96 returned:

`ETF_EU_POST_MERGE_US_DONOR_LEAK_ASSURANCE: PASS`

Reviewed frozen head:

`e5d3470e1e1ab7f402a02cb31b775f3f902d4928`

Evidence comment: `5246954887`.

## Merge and exact-main validation

PR #95 merged unchanged as:

`10823b7c457a253e409a768f52ee95b1522c363f`

Exact-main push run `31472717495`:
- product boundary SUCCESS;
- 6 planted tests passed;
- 32 active workflows scanned;
- blockers empty;
- verdict PASS.

The real merge and the previously tested synthetic merge have identical tree:

`71a614575bdc1d675ece53684d14601ce76fde90`

Therefore the workflow-authority evidence from the reviewed merge-compatibility tree applies exactly to merged code content:

`active=32 | retired=23 | candidate=1 | delivery=1 | US donor execution=0`.

No retired donor workflow re-executed on the real merge push, and both erroneous US pricing artifact paths remain absent.

## Protected state

```text
portfolio_blob=df710b5fbe4172506b67b7f591030a8c6a098c64
trade_ledger_blob=c6765ba380fe0c40272688a017dc0dc99b46d571
VWCE=151
EUNA=1526
SXR8=10
L0CK=934
cash_eur=50208.40
```

## Protected actions

```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
allocation_decision_reopened=false
```

## Definition of done

All acceptance criteria are complete. Closeout handover:

`handover/ETF_EU_POST_MERGE_US_DONOR_LEAK_REPAIR_V1_CLOSE_20260811.md`

Any next Weekly ETF EU report is a separate fresh production candidate cycle and is not part of this work package.
