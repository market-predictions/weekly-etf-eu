# Weekly ETF EU — PR #91 Assurance-Fail Repair Handover

Date: 2026-08-10
Repository: `market-predictions/weekly-etf-eu`
Parent issue: #90
Pull request: #91
Failed assurance issue: #92
Owner role: `implementation_operations`
Disposition: `HANDOVER_READY`

## Purpose
This handover freezes the implementation repair that followed the independent FAIL on PR #91 head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

Issue #92 remains the immutable assurance record for that failed candidate. It may not be reused as assurance for the repaired candidate.

## Reviewer FAIL that triggered this repair
The prior reviewer found two material blockers:

1. pricing builder, validator and normalized state did not implement one coherent v2 completed-close/funded-consensus contract;
2. NL/EN Markdown still contained hard-coded three-position/current-position copy and omitted funded L0CK.

No allocation-policy decision failed. Existing allocation-authority decisions were retained.

## Repair scope completed

### 1. Canonical pricing v2 contract
Implemented one executable contract:

`candidate request report_date → provider qualification → ucits_close_price_validation_basket_results_v2 → funded two-provider same-date consensus → shared v2 validator → v2 normalized state → candidate package`

Key changes:
- added `pricing/ucits_close_price_validation_contract_v2.py`;
- upgraded `tools/validate_ucits_close_price_validation_basket_results.py` to v2;
- added `runtime/build_etf_eu_client_grade_report_state_v2.py`;
- removed the hidden package-level legacy `min_threshold_met` / arbitrary priced-line-count release gate from `tools/build_etf_eu_routine_report_package.py`;
- bound candidate workflow pricing to exact `ETF_EU_REPORT_DATE`;
- required funded consensus at the provider boundary;
- bound validator expected report date to the candidate report date;
- persisted funded v2 pricing evidence and funded consistency in normalized state.

Negative regressions prove that v1 schema, report-date drift, one-provider funded evidence, missing funded lines and failed funded pricing consensus cannot pass silently.

### 2. State-derived Markdown delivery artifacts
Rebuilt Markdown reconciliation around current normalized state.

Key changes:
- funded count is dynamic;
- exact current funded ticker set is required;
- L0CK is mandatory whenever present in protected state;
- hard-coded VWCE/EUNA/SXR8-only current-position copy removed;
- three-position wording fails closed;
- retired strategic/phase target and fixed 7.50% reserve wording fails closed;
- discovered mixed-language NL client copy fails closed;
- `tools/validate_etf_eu_markdown_delivery_artifacts.py` validates NL/EN Markdown as first-class delivery artifacts;
- candidate workflow persists Markdown QA evidence alongside HTML/PDF QA.

### 3. Full candidate package regression
A new full package regression invokes the actual v2 package builder and generates/validates all six client artifacts:
- NL Markdown;
- NL HTML;
- NL PDF;
- EN Markdown;
- EN HTML;
- EN PDF.

The full regression also validates:
- protected four-position state;
- exact v2 pricing contract;
- funded two-provider evidence;
- persisted funded-consistency state;
- dynamic Markdown count/ticker set including L0CK;
- standalone client-grade HTML/PDF validation;
- removal of internal machine enum leakage from final client output.

## Deeper defects found and closed during end-to-end testing
The stronger end-to-end test exposed additional implementation gaps beneath the two original reviewer findings:

1. `tools/build_etf_eu_routine_report_package.py` still contained a hidden legacy v1 pricing gate. It now consumes the shared v2 pricing contract.
2. funded reconciliation metadata could be applied by the renderer but not remain authoritative in the persisted normalized state. It is now persisted/restored before final validation so renderer and validator consume one state contract.
3. internal enum `funded_model_position_active` could leak into final HTML/PDF. Final client output now maps it to client-safe language.
4. a mixed-language Dutch instruction line was detected by full client validation and is now explicitly reconciled/fail-closed.

These were implementation/output-contract defects, not new allocation decisions.

## Protected portfolio boundary
No repair commit changed protected state or the trade ledger.

Current protected portfolio remains:

| Ticker | ISIN | Venue | Shares |
|---|---|---|---:|
| VWCE | IE00BK5BQT80 | Xetra | 151 |
| EUNA | IE00BDBRDM35 | Xetra | 1,526 |
| SXR8 | IE00B5BMR087 | Xetra | 10 |
| L0CK | IE00BG0J4C88 | Xetra | 934 |

Cash remains `EUR 50,208.40`.

Protected actions during repair:

```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
```

## Allocation authority retained
The repair did not reopen or change `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md` decisions.

Still retired as current authority:
- 50% maximum position;
- 35% minimum cash;
- 15% maximum new ETF;
- 75% as position cap.

Still research/shadow only unless separately adopted:
- 25% turnover;
- 18% semiconductor/theme cap.

Donor >3%/>5% cash and ~40% factor thresholds remain review/disclosure triggers, not portfolio caps or targets.

## Validation evidence
Last fully green semantic implementation head:

`19954692ff8b33d5ffac9b09d6654210a7194997`

Exact semantic-head GitHub Actions:
- donor parity/full six-artifact package E2E: run `31433054217` — SUCCESS;
- product boundary: run `31433053898` — SUCCESS;
- release evidence preflight: run `31433054597` — SUCCESS;
- shadow CID transport validation: run `31433054225` — SUCCESS;
- strategy synchronization shadow: run `31433054231` — SUCCESS;
- target allocator shadow: run `31433054316` — SUCCESS;
- transition composition replay: run `31433054295` — SUCCESS.

The donor-parity job recorded:

```text
31 passed in 9.86s
ETF_EU_WORKFLOW_AUTHORITY=PASS
ETF_EU_CANDIDATE_PRICING_AND_MARKDOWN_WIRING=PASS
ETF_EU_DONOR_PARITY_STATIC_AUTHORITY_AUDIT=PASS
```

Pre-handover governance head:

`a9f7906df5abdaf00751552d4f950b3e13f0b778`

## Fresh assurance freeze rule
This handover and the claim transition are committed atomically as the final candidate mutation.

Because a commit cannot self-reference its own SHA, the exact fresh-assurance authority is:

> the live PR #91 head immediately after the atomic claim+handover commit containing this file.

That resulting SHA must be re-read from GitHub, must pass the required exact-head PR gates, and must then be recorded verbatim in a **new independent assurance issue distinct from #92**.

Any later PR-head mutation invalidates that assurance target and requires another fresh cycle.

## Required next assurance verdict

`ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS | FAIL | INDETERMINATE`

The fresh reviewer must independently verify at minimum:
- the former pricing blocker is closed through the actual candidate chain;
- the former Markdown/L0CK blocker is closed in actual client delivery artifacts;
- the six-artifact package E2E is meaningful and not a static-only test;
- protected four-position state is unchanged;
- allocation-authority boundaries remain intact;
- candidate/delivery role separation remains intact;
- no portfolio/ledger mutation, broker execution or report send occurred.

## Release boundary
A fresh PASS authorizes only unchanged-head merge if the project governance permits it. It does not authorize email delivery or broker execution.

After PASS and merge, exact-main validation plus project/control-plane lifecycle reconciliation remain mandatory before issue #90 and the integration claim may close.
