# ETF EU Post-Merge US Donor Leak Repair V1

Date: 2026-08-10
Parent issue: #90
Issue: #94
Pull request: #95
Claim: `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`
Owner role: `implementation_operations`
Status: `IMPLEMENTATION_COMPLETE_PENDING_FRESH_ASSURANCE`

## Current issue
Post-merge validation after independently PASSed PR #91 exposed executable US Weekly ETF donor pricing/report paths inside Weekly ETF EU.

## Root cause
Three active workflows were still coupled to donor/US output/runtime conventions:
1. `.github/workflows/persist-etf-pricing-audit.yml` executed `pricing.run_pricing_pass` and wrote generated donor pricing state back to `main`;
2. `.github/workflows/validate-etf-runtime.yml` executed the same donor pricing runtime and legacy `send_report.py` renderer;
3. `.github/workflows/validate-etf-lane-breadth.yml` validated donor `weekly_analysis_pro_*` report files rather than the current ETF EU donor-discovery → UCITS bridge.

The retained donor module itself is historical/source material, not the defect. The defect was active ETF EU workflow authority invoking it.

## Incident evidence
PR #91:
- reviewed head: `686c658c03d5ba4cbd208e254822a73b3fb514f2`;
- issue #93 verdict: PASS;
- merge: `202b0a629af34c697c7b7cb8fdce97fbb56bddbc`.

Post-merge bot commit:
- `d771bde734ffda6120a77b1f4fe0e99bd198cc96`;
- added `output/pricing/price_audit_2026-08-10_20260810_214841.json`;
- added `output/pricing/price_cache_2026-08-10.json`;
- audit contained GLD/GSG/PAVE/PPA/SMH/SPY/URNM instead of protected EU holdings VWCE/EUNA/SXR8/L0CK.

## Implemented repair
- all three legacy donor routes retained only as `.yml.disabled` audit history;
- both leaked US pricing artifacts removed from PR #95;
- `tools/validate_etf_eu_repository_boundary.py` upgraded to fail active FX or US donor execution/report tokens;
- `tools/validate_etf_eu_workflow_authority.py` scans `.yml` + `.yaml`, requires disabled copies for all retired names and rejects active donor execution/report tokens;
- planted tests verify active donor pricing and `send_report.py` are blocked while `.yml.disabled` history is ignored;
- desired donor breadth behavior remains through current EU donor discovery → UCITS mapping/fundability architecture;
- no second EU pricing/report authority was introduced.

## Exact semantic validation
Semantic baseline:

`d9b5731bbd0b125e2df9b778282116f9d8c32314`

Evidence:
- product boundary run `31436751783` — SUCCESS;
- product boundary planted tests — 6 passed;
- full product-boundary active-workflow audit — PASS;
- donor parity/full-package run `31436751773` — SUCCESS;
- full-package and blocker regression suite — 31 passed;
- workflow authority — `PASS | active_workflows=32 | retired_disabled=23 | candidate_route=1 | delivery_route=1 | us_donor_execution_routes=0`;
- candidate pricing/Markdown wiring — PASS;
- static allocation authority audit — PASS.

## Protected boundaries
```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
allocation_decision_reopened=false
```

Protected EU state and trade ledger are unchanged.

## Acceptance criteria status
- three donor/legacy workflows non-executable and present as `.disabled`: PASS;
- leaked US audit/cache absent from repaired candidate: PASS;
- active donor execution/report token scan: PASS;
- product-boundary negative tests: PASS;
- workflow-authority gate: PASS;
- canonical candidate route unchanged: PASS;
- sole real delivery route unchanged: PASS;
- protected portfolio/ledger unchanged: PASS;
- fresh independent assurance: PENDING.

## Definition of done remaining
1. freeze exact PR #95 head after atomic handover commit;
2. independent `governance_release_assurance` verdict on exact frozen head;
3. merge only after PASS and unchanged head;
4. exact-main product/workflow boundary PASS;
5. verify no US donor artifact regeneration;
6. close issue #94, parent issue #90 and claim;
7. reconcile central Control state.

This work package does not authorize report delivery or broker execution.
