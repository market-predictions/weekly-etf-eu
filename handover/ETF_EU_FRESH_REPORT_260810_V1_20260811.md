# ETF EU Fresh Report 260810 V1 — Implementation Handover

Date: 2026-08-11
Role: `implementation_operations`
Issue: #97
PR: #98
Branch: `agent/etf-eu-fresh-260810-v1`
Report date: `2026-08-10`
Run ID: `20260810_123000`
Status: `IMPLEMENTATION_COMPLETE_PENDING_INDEPENDENT_ASSURANCE`

## Governance binding
This handover is an evidence index, not an assurance verdict and not delivery authority.

The independently reviewed frozen head MUST be taken from the live PR #98 head recorded in the dedicated assurance issue immediately after exact-head CI is green. If the PR head changes after that freeze, the assurance verdict is invalid and must become `INDETERMINATE` or be rerun on the new head.

Implementation content immediately preceding this handover commit was green on exact head:

`524f3da1792675567fbae4b8ee1ba2bc2515a4df`

The handover commit itself changes only this evidence index. Its resulting live PR head must therefore be revalidated and is the candidate eligible for freeze.

## Delivered candidate

```text
report_date=2026-08-10
run_id=20260810_123000
model_portfolio_only=true
real_broker_execution=false
funded_positions=6
cash_eur=28101.01
invested_market_value_eur=72637.72
nav_eur=100738.73
```

Funded positions:

| Ticker | Shares | Change this run |
|---|---:|---|
| VWCE | 151 | hold/revalue |
| EUNA | 1,526 | hold/revalue |
| SXR8 | 10 | hold/revalue |
| L0CK | 934 | hold/revalue |
| DFEN | 207 | **added** |
| IQQQ | 149 | **added** |

Current allocation decision:

`output/activation/etf_eu_current_allocation_decision_20260810_123000.json`

No real broker order was placed.

## Decision framework
- position count was not a target;
- 50% max-position, 35% min-cash and 15% max-new-ETF are retired unsupported shadow rules;
- donor 25% turnover and 18% semiconductor values remain research/shadow only;
- donor U.S.-portfolio funding labels are not EU allocation authority;
- current EU allocation requires EU-local re-underwriting, exact identity/KID/trading line, completed-close evidence and an explicit current allocation decision;
- remaining cash is deploy-or-explain opportunity cash, not a fixed reserve floor.

## Input/state contract
Current completed-close pricing date is 2026-08-10.

Funded valuation requirement: exact-line two-provider completed-close consensus.

Final funded valuation coverage: `6/6`.

Broad discovery evidence:
- donor breadth: 12 required buckets;
- 25 assessed donor lanes;
- donor→UCITS mapping/fundability bridge;
- nonfunded mapping/pricing remains research-only and creates no funding authority.

Exact trading-line identity is `(ISIN,ticker)` where required; shared ISIN across SXR8/CSPX no longer collapses distinct trading lines.

## Output contract
Final NL/EN package includes:
- Markdown;
- HTML;
- PDF;
- normalized report state;
- recommendation scorecard;
- donor discovery bridge;
- machine validation artifacts;
- PDF review pages.

Permanent output-semantics controls:
- `runtime/finalize_etf_eu_markdown_semantics.py`
- `runtime/finalize_etf_eu_client_surface_semantics.py`
- `tools/build_etf_eu_routine_report_package_v2.py`

These prevent legacy renderer copy from contradicting current allocation/pricing state and prevent Dutch output from retaining known English donor fragments.

## Operational runbook / workflow state
Canonical current candidate route:

`.github/workflows/run-weekly-etf-eu-routine.yml`

The route now contains:
- donor repo checkout and latest eligible lane selection;
- EU-local broad discovery bridge;
- quota-aware allocation-candidate pricing selection;
- Alpha Vantage + Yahoo current completed-close evidence;
- v2 normalized package build;
- strict NL/EN MD/HTML/PDF validation;
- PDF review rendering;
- candidate-only persistence.

It has no report-delivery authority.

Sole delivery route remains separate:

`.github/workflows/send-weekly-etf-eu-controlled-transport.yml`

Temporary branch-only rerender workflow was removed before assurance.
Temporary issue-#97 push trigger was removed from the canonical candidate route before assurance.

Historical transition-era PR gates were retired to `.disabled` evidence because they enforced non-authoritative legacy composition against current model state:
- `validate-etf-eu-target-allocator-shadow.yml.disabled`
- `validate-etf-eu-transition-replay.yml.disabled`

Their historical builders/validators/evidence remain available for reproducibility but have no current allocation/funding authority.

## Validation evidence before handover commit
Exact implementation head `524f3da1792675567fbae4b8ee1ba2bc2515a4df`:
- donor parity run `31505320153` — PASS;
- multi-provider pricing run `31505320397` — PASS;
- product boundary run `31505320409` — PASS;
- release evidence preflight run `31505320379` — PASS;
- Stooq connectivity diagnostic run `31505320172` — PASS.

Final semantic package rerender:
- run `31502986816` — PASS through state, package, strict NL/EN validation, semantic assertions, PDF review and branch persist.

The handover head itself must receive fresh exact-head CI before freeze.

## Material implementation repairs in this cycle
1. Broad donor discovery wired into canonical production candidate flow.
2. Explicit allocation-candidate second-source pricing removes the pre-funding evidence deadlock.
3. Alpha Vantage secret wiring corrected.
4. Governed Alpha capacity policy tested for funded vs explicit candidate usage.
5. Shared-ISIN exact-line validator defect repaired.
6. Donor U.S. fundability label removed as EU funding authority.
7. Current completed-close revaluation precedes allocation sizing.
8. Explicit model-only allocation added DFEN/IQQQ.
9. Current allocation lineage/cash classification preserved in normalized state.
10. MD/HTML/PDF semantic divergence repaired state-first and fail-closed.
11. Dutch language leakage repaired and regression-gated.
12. Obsolete transition/shadow PR gates retired from current authority.
13. Donor discovery bridge regression updated to current v2 two-provider pricing schema with a negative single-source test.

## Protected boundaries for assurance
Independent reviewer must verify:

```text
real_broker_execution=false
report_delivery=false
smtp_send=false
candidate_delivery_authority=false
mapping_is_funding_authority=false
pricing_is_funding_authority=false
explicit_allocation_decision_required=true
```

The reviewer must also independently verify the protected six-position state, exact current pricing evidence, current allocation decision, full active workflow topology, current output semantics and that historical shadow gates are non-executable.

## Required next step
Fresh independent `governance_release_assurance` on the exact unchanged PR #98 frozen head.

PASS may authorize only the governance-controlled merge of that exact unchanged head. It does not authorize SMTP, delivery, real broker execution or further portfolio mutation.
