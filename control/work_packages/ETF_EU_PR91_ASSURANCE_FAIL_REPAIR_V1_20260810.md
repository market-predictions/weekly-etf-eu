# ETF EU PR91 Assurance-Fail Repair V1

Date: 2026-08-10
Parent work package: `ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1`
Parent issue: #90
Failed assurance issue: #92
Pull request: #91
Owner role: `implementation_operations`
Status: `IMPLEMENTATION_COMPLETE_PENDING_FRESH_ASSURANCE`

## Trigger
Independent role-B assurance returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

on frozen head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

The failed head remains historical assurance evidence. It is not merge-authorized and not delivery-authorized.

## Repair result

All three accepted repair scopes are implemented on the replacement semantic baseline:

`19954692ff8b33d5ffac9b09d6654210a7194997`

This SHA is the last fully green semantic implementation baseline before governance/handover-only closeout commits.

### P0-A — Canonical pricing v2 contract — COMPLETE

Canonical executable chain:

`candidate request report_date → provider qualification → ucits_close_price_validation_basket_results_v2 → funded two-provider consensus → shared v2 validator → v2 normalized state → candidate package`

Implemented evidence:
- `pricing/ucits_close_price_validation_contract_v2.py`;
- `tools/validate_ucits_close_price_validation_basket_results.py`;
- `runtime/build_etf_eu_client_grade_report_state_v2.py`;
- `tools/build_etf_eu_routine_report_package.py` no longer requires legacy `min_threshold_met` or an arbitrary priced-line-count release gate;
- `tools/build_etf_eu_routine_report_package_v2.py` consumes the v2 state builder;
- `.github/workflows/run-weekly-etf-eu-routine.yml` passes exact `--report-date`, requires funded consensus and validates the same report date.

Negative regressions prove that v1 schema, report-date drift, one-provider funded evidence and failed funded consensus do not pass.

### P0-B — State-derived Markdown delivery artifacts — COMPLETE

Implemented evidence:
- `runtime/reconcile_etf_eu_funded_markdown.py` derives funded count/ticker set from current normalized state;
- all four funded tickers are required, including L0CK;
- three-position wording, retired strategic/phase targets, fixed 7.50% reserve wording and the discovered mixed-language NL leakage fail closed;
- `tools/validate_etf_eu_markdown_delivery_artifacts.py` validates NL and EN Markdown as delivery artifacts;
- candidate workflow persists Markdown QA evidence alongside HTML/PDF evidence.

### P0-C — Real end-to-end candidate regression — COMPLETE

The release regression now invokes the real v2 candidate package builder and produces/validates all six client artifacts:
- NL MD;
- NL HTML;
- NL PDF;
- EN MD;
- EN HTML;
- EN PDF.

The regression also validates:
- protected four-position state;
- canonical v2 pricing state;
- funded two-provider evidence;
- dynamic Markdown including L0CK;
- real client-grade HTML/PDF validator;
- persisted funded-consistency metadata;
- client-safe status labels rather than internal enum leakage.

Primary tests:
- `tests/test_etf_eu_pricing_v2_and_markdown_delivery.py`;
- `tests/test_etf_eu_candidate_build_end_to_end.py`;
- `tests/test_etf_eu_full_candidate_package_end_to_end.py`.

## Exact semantic-baseline evidence

Semantic implementation head:

`19954692ff8b33d5ffac9b09d6654210a7194997`

Exact-head GitHub Actions:
- donor parity/full package E2E `31433054217` — SUCCESS, 31 tests passed;
- product boundary `31433053898` — SUCCESS;
- release evidence preflight `31433054597` — SUCCESS;
- shadow CID transport validation `31433054225` — SUCCESS;
- strategy synchronization shadow `31433054231` — SUCCESS;
- target allocator shadow `31433054316` — SUCCESS;
- transition composition replay `31433054295` — SUCCESS.

The donor-parity job additionally reported:

```text
31 passed
ETF_EU_WORKFLOW_AUTHORITY=PASS
ETF_EU_CANDIDATE_PRICING_AND_MARKDOWN_WIRING=PASS
ETF_EU_DONOR_PARITY_STATIC_AUTHORITY_AUDIT=PASS
```

## Protected boundaries
Throughout this repair:
- portfolio mutation = false;
- trade-ledger write = false;
- real broker execution = false;
- report delivery = false;
- SMTP send = false;
- existing allocation-authority decisions remain unchanged.

## Handover and assurance
Remaining work is governance-only:
1. reconcile roadmap/current state/next actions/claim around the completed repair;
2. write a new repair implementation handover as the final candidate mutation;
3. freeze the resulting exact PR #91 head;
4. open a fresh independent assurance issue distinct from #92;
5. require `ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_REVERIFY: PASS | FAIL | INDETERMINATE`;
6. merge only after PASS and unchanged head.

Issue #92 remains the immutable assurance record for the failed historical head and may not be reused for the replacement candidate.
