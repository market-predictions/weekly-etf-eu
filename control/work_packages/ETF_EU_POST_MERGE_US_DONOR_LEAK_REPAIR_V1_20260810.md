# ETF EU Post-Merge US Donor Leak Repair V1

Date: 2026-08-10
Parent issue: #90
Issue: #94
Pull request: #95
Claim: `ETF-EU-POST-MERGE-US-DONOR-LEAK-REPAIR-V1`
Owner role: `implementation_operations`
Status: `ACTIVE`

## Current issue
Post-merge validation after independently PASSed PR #91 exposed an active US Weekly ETF donor pricing/report runtime inside the Weekly ETF EU Actions topology.

## Root cause
Two active workflows invoked donor/US execution surfaces:
- `.github/workflows/persist-etf-pricing-audit.yml` → `pricing.run_pricing_pass` and write-back to `main`;
- `.github/workflows/validate-etf-runtime.yml` → `pricing.run_pricing_pass` plus legacy `send_report.py` rendering.

The retained donor module defaults to `output/etf_portfolio_state.json`, `weekly_analysis_pro_*.md` and U.S.-close semantics. The repository-boundary gate guarded FX leakage but not US Weekly ETF donor-runtime leakage.

## Required change
1. Retire both workflows as `.yml.disabled` historical evidence.
2. Delete the two US artifacts introduced by bot commit `d771bde734ffda6120a77b1f4fe0e99bd198cc96` from the repaired candidate.
3. Extend repository-boundary validation to reject donor-only execution tokens in active `.yml/.yaml` workflows.
4. Extend workflow-authority validation with the same fail-closed boundary and require both retired routes to remain disabled.
5. Add planted negative tests proving active donor pricing/report invocation fails while `.yml.disabled` history is ignored.
6. Update workflow authority documentation and project lifecycle records.
7. Run exact-head CI and inspect failures for additional active donor leaks.
8. Freeze the exact candidate and obtain new independent `governance_release_assurance` before merge.
9. Perform exact-main validation after merge before parent issue #90 and the successor claim close.

## Acceptance criteria
- `persist-etf-pricing-audit.yml` absent as active workflow and present as `.yml.disabled` audit history.
- `validate-etf-runtime.yml` absent as active workflow and present as `.yml.disabled` audit history.
- leaked `price_audit_2026-08-10_20260810_214841.json` and `price_cache_2026-08-10.json` absent from repaired candidate.
- product-boundary validator fails a planted active `pricing.run_pricing_pass` workflow.
- product-boundary validator fails planted active legacy `send_report.py` workflow.
- product-boundary validator does not treat `.yml.disabled` history as executable.
- workflow-authority validator reports zero US donor execution routes.
- canonical candidate route remains `.github/workflows/run-weekly-etf-eu-routine.yml`.
- sole real delivery route remains `.github/workflows/send-weekly-etf-eu-controlled-transport.yml`.
- protected portfolio/ledger unchanged.
- fresh independent PASS required on exact PR #95 head.

## Non-goals
- do not delete historical donor modules solely because they exist;
- do not create a second EU pricing engine;
- do not reopen allocation policy;
- do not generate or send the next weekly report in this repair package;
- do not perform broker execution.

## Definition of done
```text
implementation exact-head green
+ independent assurance PASS on unchanged PR #95 head
+ merge
+ exact-main product/workflow boundary green
+ no US donor artifact regeneration
+ project/control-plane lifecycle reconciled
+ parent issue #90 and claim closed only then
```
