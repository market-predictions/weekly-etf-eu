# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-10
repository=market-predictions/weekly-etf-eu
main_sha_at_reconciliation=3d97712a9bd135192f67b8c5dd860d295adbf5fc
operating_mode=DONOR_PARITY_RECONCILIATION_WITH_INDEPENDENT_RELEASE_ASSURANCE
parent_work_package=ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1
repair_work_package=ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_V1
active_claim=ETF-EU-DONOR-PARITY-RECONCILIATION-V1
working_branch=agent/etf-eu-donor-parity-reconciliation-v1
pull_request=91
parent_issue=90
failed_assurance_issue=92
state=ASSURANCE_FAIL_IMPLEMENTATION_REPAIR_ACTIVE
principal_decision_required=false
principal_action_required=false
merge_authorized=false
delivery_authorized=false
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

## Assurance outcome

Independent `governance_release_assurance` reviewed frozen PR #91 head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

and returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

Issue #92 is the immutable assurance record for that failed candidate. The failed SHA must never be treated as merge- or delivery-authorized.

The review confirmed the donor-parity allocation/state decisions and protected portfolio boundaries, but found two executable release blockers below.

## P0 blocker A — pricing v2 execution contract

The failed candidate mixed three incompatible expectations:
- provider builder emitted `ucits_close_price_validation_basket_results_v2`;
- validator required v1;
- normalized state still relied on historical `min_threshold_met`.

The candidate workflow also failed to bind provider pricing explicitly to `ETF_EU_REPORT_DATE` and did not require funded consensus at the provider boundary.

Repair authority:
- `pricing/ucits_close_price_validation_contract_v2.py`
- `tools/validate_ucits_close_price_validation_basket_results.py`
- `runtime/build_etf_eu_client_grade_report_state_v2.py`
- `.github/workflows/run-weekly-etf-eu-routine.yml`

Required current behavior:

```text
candidate request report_date
→ provider qualification on that exact date
→ ucits_close_price_validation_basket_results_v2
→ funded two-provider consensus + exact-line identity gate
→ v2 validator
→ v2 normalized state
→ candidate package
```

Any v1 schema, report-date drift, missing funded line, one-provider funded evidence or failed funded pricing gate must fail closed.

## P0 blocker B — Markdown delivery-state consistency

The failed candidate still had a hard-coded Markdown reconciliation path that could state `three funded UCITS positions`, omit L0CK and describe only VWCE/EUNA/SXR8 even though protected state contains four funded positions.

Repair authority:
- `runtime/reconcile_etf_eu_funded_markdown.py`
- `tools/validate_etf_eu_markdown_delivery_artifacts.py`
- `.github/workflows/run-weekly-etf-eu-routine.yml`

Required current behavior:
- NL/EN Markdown funded count is dynamic from protected/current normalized state;
- funded ticker set is dynamic and includes L0CK;
- retired three-position, strategic/phase-target and fixed 7.50% reserve wording fails closed;
- Markdown is validated as a real delivery artifact, not merely an audit companion.

## Protected portfolio authority

Authority remains:

`output/etf_eu_portfolio_state.json`

| Ticker | ISIN | Venue | Shares |
|---|---|---|---:|
| VWCE | IE00BK5BQT80 | Xetra | 151 |
| EUNA | IE00BDBRDM35 | Xetra | 1,526 |
| SXR8 | IE00B5BMR087 | Xetra | 10 |
| L0CK | IE00BG0J4C88 | Xetra | 934 |

```text
cash_eur=50208.40
funded_position_count=4
model_portfolio_only=true
real_broker_execution=false
```

This assurance-fail repair does not reopen allocation decisions and may not change shares, cash or the trade ledger.

## Allocation authority retained from the passed scope

Canonical contract:

`control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`

Still retired as current authority:

```text
50% maximum position
35% minimum cash
15% maximum new ETF
75% as a position cap
```

Still research/shadow only unless separately adopted:

```text
25% turnover
18% AI-compute/semiconductor cap
```

Donor cash >3%/>5% and ~40% factor thresholds remain review/disclosure triggers, not allocation caps or target weights.

No new stable allocation decision is needed in `DECISION_LOG.md` for this repair.

## Workflow/release boundary

PR #91 has been returned to draft implementation state. Any semantic repair creates a new candidate/head SHA and invalidates the earlier assurance cycle.

Required sequence:

```text
repair both blockers
→ executable end-to-end candidate regression
→ all exact-head PR gates green
→ new implementation handover
→ freeze new PR #91 head
→ fresh independent assurance in a new issue
→ merge only after PASS + unchanged head
→ exact-main validation and lifecycle closeout
→ separate fresh-report production cycle
→ separate guarded delivery authority
```

No email send or broker execution is authorized by this repair mandate.
