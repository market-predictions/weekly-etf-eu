# ETF EU synchronization output-contract repair decision

**Date:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/donor-report-parity`  
**Pull request:** #66  
**Status:** accepted for the shadow architecture; no activation authority

## Decision

The synchronized ETF EU sister report must apply a final explicit output-contract layer after allocator, candidate-visibility, localization, compaction and pagination overlays.

That final layer must restore and validate the client-visible donor section/table contract without changing strategy, allocation, valuation or authority state.

## Root cause

The underlying synchronization and allocator artifacts were valid, but late report transformations caused four output defects:

1. donor table headers drifted in Sections 2, 4 and 11;
2. the compact Section 14 intentionally removed a duplicate incumbent table while an older validator still required it;
3. the final-action table carried multiple CSS classes while a validator expected one exact class string;
4. internal exposure IDs in HTML metadata were incorrectly classified as visible client-text leaks.

Restoring the donor headers increased Dutch pagination enough to create one orphaned performance row. A presentation-only curve/performance compaction was therefore required to preserve the accepted 11-page bilingual contract.

## Chosen architecture

```text
immutable donor contract
→ synchronization state
→ policy allocator
→ report renderer
→ portfolio alignment
→ allocator surface
→ incumbent overlap
→ client-language normalization
→ policy reconciliation
→ compact transition surface
→ presentation-only layout fix
→ operational pagination
→ final output-contract layer
→ validation bundle
```

Canonical finalizer:

```text
runtime/finalize_etf_eu_report_output_contract.py
```

## Stable validation rules

1. Scan only visible client text for internal implementation tokens; HTML metadata remains machine-readable evidence.
2. Validate CSS class membership, not exact single-class serialization.
3. Treat the removed Section 14 incumbent table as valid only when the compaction manifest proves that incumbent evidence remains in Sections 10, 13 and 15.
4. Preserve the donor table-header contract after all late overlays.
5. Preserve candidate markers and portfolio-alignment lineage.
6. Require matching Dutch and English 11-page PDFs.
7. Never weaken portfolio, funding, execution, activation or delivery authority gates to make an output validator pass.

## Validated evidence

```text
validated_code_head=034b5f93056d36dfc7a6048b43b650ff434c0516
allocator_report_workflow_run=30499071087
artifact_id=8742768136
artifact_digest=sha256:f6cad390bc41502f40b7d38cd14f83f34734c63f3e65cb15093ef3474a3f16d2
validation_bundle_valid=true
nl_page_count=11
en_page_count=11
machine_blockers=[]
visual_review_passed=true
```

All current PR workflows at the validated code head completed successfully.

## Authority boundary

```text
portfolio_mutation=false
ledger_write=false
funding_authority=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
```

This decision accepts the output-contract repair as part of the shadow architecture only. It does not authorize Stage 1, Stage 2, production-report replacement, portfolio mutation, a trade, or a new email delivery.

## Consequence

PR #66 is technically ready for four-layer architecture review. The next action remains review and potential squash merge of the shadow architecture without activation. Fresh cutover evidence and any Stage-1 authorization belong in the separate WP-SYNC-09 decision package.
