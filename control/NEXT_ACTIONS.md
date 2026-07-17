# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
DISPATCH_AND_VERIFY_CORRECTED_VISUAL_PREVIEW_20260717_123500
```

## Completed model state

```text
broker_neutral_first_tranche_activation_closed=true
position_count=3
cash_eur=60439.44
invested_market_value_eur=39577.16
nav_eur=100016.60
real_broker_execution=false
production_delivery=false
```

| Ticker | Role | Shares | Value | Weight | Current action |
|---|---|---:|---:|---:|---|
| VWCE | Global core | 151 | €24,963.32 | 24.959177% | Hold after first tranche |
| EUNA | Aggregate-bond stabiliser | 1,526 | €7,497.24 | 7.495996% | Hold after first tranche |
| SXR8 | U.S. equity overweight | 10 | €7,116.60 | 7.115419% | Hold; no second tranche |

No automatic add, reduce, exit, later tranche or satellite activation is authorised.

## Rejected preview — do not use

```text
run_id=20260717_114500
github_workflow_run_id=29571969253
report_suffix=260717_04
workflow_result=success
machine_validation_passed=true
visual_review_passed=false
client_grade_preview_accepted=false
superseded=true
```

The package passed all machine gates but failed visual acceptance because of equity-curve date-label overlap, funded-position table wrapping and an untranslated Dutch valuation-history comment.

Evidence:

```text
output/quality/etf_eu_client_grade_v2_validation_20260717_114500.json
output/quality/etf_eu_routine_pdf_visual_review_20260717_114500.json
output/run_manifests/etf_eu_routine_preview_manifest_20260717_114500.json
```

Do not send, promote, repair in place or reuse this run identity.

## Corrected preview ready for dispatch

```text
workflow_name=ETF EU - Generate and Validate Preview (NO EMAIL)
branch=main
request_path=control/run_queue/etf_eu_routine_preview_request_20260717_123500.md
run_id=20260717_123500
report_date=2026-07-17
report_suffix=260717_05
```

The connector-authored queue push did not produce a verifiable Actions run. Manually dispatch this workflow once. Do not use `Re-run jobs` on an older preview because a rerun remains pinned to the older commit and workflow definition.

## Required corrected-run sequence

```text
1. run tests/test_etf_eu_cap01.py, including funded-state, ISIN and visual-contract regressions;
2. obtain current exact-line UCITS pricing evidence;
3. refresh donor macro context and adapt it for EU use;
4. read output/etf_eu_portfolio_state.json as quantity and cash authority;
5. update the report-date valuation observation deterministically;
6. build the normalized funded-aware report state;
7. render Dutch-primary and English-companion HTML/PDF;
8. enforce strict funded-state and semantic ISIN gates;
9. render all pages for complete visual review;
10. persist preview and review evidence;
11. perform no transport or email send.
```

## Corrected output requirements

The report must consistently show:

```text
3 active model positions
VWCE 151 shares
EUNA 1526 shares
SXR8 10 shares
cash EUR 60,439.44
NAV EUR 100,016.60
pricing date for every funded position
funded ISIN identity strip in Dutch and English
non-overlapping first/last equity-curve date labels
no arbitrary wrapping of ticker, ISIN, price or date cells
Dutch valuation-history comments in Dutch
VWCE, EUNA and SXR8 lanes marked funded and active
SXR8 second tranche not authorised
unfunded satellites separated from funded holdings
broker-neutral model-investability language
active equity curve reconciled to valuation history and NAV
```

The following must fail acceptance:

```text
first model position active
first model purchase executed
VWCE not funded
EUNA not funded
broker availability as a model-investability gate
three funded positions with singular cockpit or conclusion copy
overlapping adjacent equity-curve date labels
funded identifiers broken across arbitrary lines
English operational comments in the Dutch report
```

## Review after the corrected run

Review all six Dutch and all six English PDF pages for:

- clipping, overlap and orphaned headings;
- readable wide, pricing and funded-position tables;
- correct Unicode and language consistency;
- exact reconciliation of quantities, cash, invested value and NAV;
- visible pricing dates and model-only disclosures;
- correct active status for VWCE, EUNA and SXR8;
- no stale activation or broker-dependent model wording;
- truthful overlap and contribution language;
- equity-curve visibility, NAV reconciliation and non-overlapping labels.

Only after complete visual review may the review artifact state:

```text
visual_review_passed=true
content_consistency_passed=true
client_grade_preview_accepted=true
blockers=[]
```

## After preview acceptance

Preview acceptance does not authorize delivery. A separate explicit delivery instruction is required before opening the guarded production-delivery workflow. Delivery success requires real transport evidence and independent receipt confirmation.

## Later portfolio monitoring

For each later routine cycle determine separately:

1. whether VWCE remains a valid global-core holding;
2. whether EUNA continues to provide the intended stabilising role;
3. whether SXR8 remains a justified U.S. overweight;
4. contribution and relative strength since activation;
5. overlap between VWCE embedded U.S. exposure and direct SXR8 exposure;
6. whether remaining cash is still blocked capacity or warrants a separately authorised tranche.

## Candidate development after preview acceptance

### SXRV

```text
strategic_target_weight_pct=7.5
current_status=blocked_not_funded
```

Require exact-line identity, fresh EUR pricing, concentration and overlap review, and a separate allocation decision.

### Semiconductor satellite

```text
strategic_target_weight_pct=5.0
current_status=blocked_not_funded
```

Require a verified UCITS exchange line, fresh pricing, concentration review and an approved EUR/FX model-execution policy. Broker permission is not a model gate.

## Broker and delivery boundaries

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
real_order_authority=false
production_delivery_authority=false
```

Only a contemplated real order may open an optional broker adapter. Only a separate explicit delivery instruction may open the guarded delivery path.

## Closed identities

Do not reuse:

```text
run_id=20260716_012900
review_run_id=20260716_092600
broker_neutral_review_run_id=20260716_205500
rejected_preview_run_id=20260716_214500
rejected_preview_run_id=20260717_005500
rejected_preview_run_id=20260717_011500
rejected_preview_run_id=20260717_112500
rejected_preview_run_id=20260717_114500
report_suffix=260716
report_suffix=260716_02
report_suffix=260717
report_suffix=260717_02
report_suffix=260717_03
report_suffix=260717_04
```

## Development rule

Repair concrete funded-aware report defects directly and strengthen validators or regressions when a defect escapes a green gate. Do not create another architecture package unless a material new capability is required.
