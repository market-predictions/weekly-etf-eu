# Handover — Weekly ETF EU synchronized report output-contract repair

**Date:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/donor-report-parity`  
**Pull request:** #66  
**Status:** completed and validated; shadow architecture only

## Current issue

The allocator report workflow failed after later WP-SYNC overlays even though synchronization, allocation and authority artifacts were valid.

Observed failures included:

- drift from required donor table headers;
- a validator requiring a duplicate incumbent table removed by intentional compaction;
- brittle exact-class matching for the final alignment table;
- HTML metadata identifiers misclassified as visible client text;
- a Dutch-only orphaned performance row creating a twelfth page.

## Root cause

The report pipeline had no final authoritative output-contract pass after all allocator, localization, compaction and pagination steps. Individual overlays were locally valid but collectively allowed client-surface drift.

## Implemented change

### Final output-contract layer

Added:

```text
runtime/finalize_etf_eu_report_output_contract.py
```

It:

- restores donor header contracts in Sections 2, 4 and 11;
- preserves candidate markers and alignment lineage;
- removes internal blocker codes from visible text;
- normalizes the final-action table class contract;
- re-renders both PDFs;
- records false mutation/funding/execution authority flags.

### Validator corrections

Updated:

```text
tools/validate_etf_eu_target_allocator_report_surface_v3.py
tools/validate_etf_eu_sister_report_shadow.py
```

The validators now:

- recognize the intentional compact Section 14 contract;
- require evidence lineage for removed duplicate content;
- validate class membership rather than exact class serialization;
- inspect visible client text rather than HTML attributes for internal-token leaks;
- require the final output-contract marker and false authority flags.

### Pagination correction

Updated:

```text
runtime/fix_etf_eu_sister_report_layout.py
```

The four-point equity curve and three-row position-performance table were compacted without deleting evidence or changing values. Both languages now render to 11 pages.

### Workflow integration

Updated:

```text
.github/workflows/validate-etf-eu-allocator-report-shadow.yml
```

The finalizer now runs before the validation bundle, and layout changes explicitly trigger the workflow.

## Validation result

Validated code head:

```text
034b5f93056d36dfc7a6048b43b650ff434c0516
```

Allocator report workflow:

```text
run_id=30499071087
conclusion=success
artifact_id=8742768136
artifact_digest=sha256:f6cad390bc41502f40b7d38cd14f83f34734c63f3e65cb15093ef3474a3f16d2
```

Validation bundle:

```text
allocator_surface=true
incumbent_overlap_surface=true
policy_reconciliation=true
promoted_candidate_visibility=true
transition_compaction=true
pagination_contract=true
pdf_layout=true
sister_report_contract=true
donor_surface_contract=true
blockers=[]
```

PDF evidence:

```text
nl_page_count=11
en_page_count=11
blank_pages=0
orphaned_rows=0
visual_review_passed=true
```

All current workflows at the validated code head are green:

```text
30499071074 strategy synchronization
30499071060 cutover product evidence
30499071076 target allocator
30499071107 transition composition replay
30499071087 allocator report
30499071090 shadow CID transport
30499071109 shadow CID live-delivery validation
30499071071 blocked activation package
```

## Official state preservation

The official portfolio and ledger were not changed:

```text
nav_eur=99756.76
cash_eur=60439.44
positions=VWCE 151, EUNA 1526, SXR8 10
portfolio_mutation=false
ledger_write=false
```

No report was sent and no activation was performed during this repair.

## Exact files added or materially changed

```text
runtime/finalize_etf_eu_report_output_contract.py
runtime/fix_etf_eu_sister_report_layout.py
tools/validate_etf_eu_target_allocator_report_surface_v3.py
tools/validate_etf_eu_sister_report_shadow.py
.github/workflows/validate-etf-eu-allocator-report-shadow.yml
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/decisions/ETF_EU_SYNC_OUTPUT_CONTRACT_REPAIR_DECISION_20260730.md
control/handovers/HANDOVER_WEEKLY_ETF_EU_OUTPUT_CONTRACT_REPAIR_20260730.md
```

## Next safe action

Review PR #66 as four separate architecture layers and decide whether to squash merge the shadow architecture into `main`.

Do not combine that review with:

- Stage-1 activation;
- Stage-2 activation;
- official portfolio or ledger mutation;
- production-report replacement;
- production delivery.

After architecture acceptance, WP-SYNC-09 must collect fresh Xetra valuation/spread evidence for VVSM and LOCK, the exact LOCK KID, current donor re-underwriting and a separate activation decision.
