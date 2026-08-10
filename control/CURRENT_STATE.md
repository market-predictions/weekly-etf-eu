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
state=REPAIR_IMPLEMENTATION_COMPLETE_PRE_HANDOVER
last_green_semantic_head=19954692ff8b33d5ffac9b09d6654210a7194997
principal_decision_required=false
principal_action_required=false
merge_authorized=false
delivery_authorized=false
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

## Assurance history

Independent issue #92 reviewed frozen PR #91 head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

and returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

Issue #92 is closed as the immutable assurance record for that failed candidate. The failed SHA has no merge or delivery authority and cannot be reused for the repaired candidate.

The review confirmed the existing donor-parity allocation/state decisions and protected boundaries. It found two executable blockers: pricing-contract incoherence and stale three-position Markdown delivery copy.

## Repair outcome — COMPLETE

### Pricing v2
Canonical candidate chain is now:

```text
candidate request report_date
→ provider qualification on exact report_date
→ ucits_close_price_validation_basket_results_v2
→ funded two-provider same-date consensus
→ shared v2 validator
→ v2 normalized state
→ candidate package
```

The candidate workflow passes the exact report date, requires funded consensus and validates against the same report date. V1 schema, report-date drift, one-provider funded evidence, missing funded lines and a failed funded pricing gate fail closed.

The hidden package-level legacy `min_threshold_met`/priced-line-count release gate has been removed. Persisted normalized state carries funded v2 pricing evidence and funded-consistency metadata.

### Markdown/output consistency
NL and EN Markdown are now state-derived delivery artifacts:
- funded count is dynamic;
- exact funded ticker set includes VWCE, EUNA, SXR8 and L0CK;
- hard-coded three-position copy is removed;
- retired strategic/phase targets and fixed 7.50% reserve wording fail closed;
- mixed-language NL leakage fails closed;
- Markdown has its own strict candidate QA artifact;
- final HTML/PDF normalizes internal funded-status enums to client-safe labels.

### Real end-to-end candidate regression
The donor-parity release regression invokes the real v2 package builder and generates/validates all six client artifacts: NL/EN MD, HTML and PDF.

Exact semantic-baseline evidence for `19954692ff8b33d5ffac9b09d6654210a7194997`:
- donor parity/full package E2E `31433054217` — SUCCESS, 31 tests passed;
- product boundary `31433053898` — SUCCESS;
- release evidence preflight `31433054597` — SUCCESS;
- shadow CID transport `31433054225` — SUCCESS;
- strategy synchronization shadow `31433054231` — SUCCESS;
- target allocator shadow `31433054316` — SUCCESS;
- transition composition replay `31433054295` — SUCCESS.

The donor-parity job also reports:

```text
ETF_EU_WORKFLOW_AUTHORITY=PASS
ETF_EU_CANDIDATE_PRICING_AND_MARKDOWN_WIRING=PASS
ETF_EU_DONOR_PARITY_STATIC_AUTHORITY_AUDIT=PASS
```

## Protected portfolio authority

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

No repair commit changed protected shares, cash or the trade ledger.

## Allocation authority — NOT REOPENED

`control/ETF_EU_ALLOCATION_AUTHORITY_V1.md` remains canonical.

Retired current authority:
```text
50% maximum position
35% minimum cash
15% maximum new ETF
75% as a position cap
```

Research/shadow only unless separately adopted:
```text
25% turnover
18% AI-compute/semiconductor cap
```

Donor cash >3%/>5% and ~40% factor thresholds remain review/disclosure triggers, not allocation caps or targets. No new stable allocation decision is required for this repair.

## Current release boundary

Product implementation is complete. Remaining work is governance-only:

```text
reconcile claim/next-actions/changelog
→ final repair handover commit
→ freeze resulting PR #91 SHA
→ fresh independent assurance in a new issue
→ merge only after PASS + unchanged head
→ exact-main validation and lifecycle closeout
```

No email send or broker execution is authorized by this repair mandate.
