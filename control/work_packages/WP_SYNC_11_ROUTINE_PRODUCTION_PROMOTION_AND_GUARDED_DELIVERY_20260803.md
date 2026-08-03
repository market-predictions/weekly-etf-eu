# WP-SYNC-11 — Routine production promotion and guarded delivery

**Date opened:** 2026-08-03  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/wp11-routine-production-promotion`  
**Status:** claimed and in progress  
**Claimed by:** ChatGPT autonomous development session

## Current issue

WP-SYNC-10 installed a validated premium production-convergence engine, but the authoritative routine runbook and package builder still point to the older 15-section funded-aware renderer.

Consequences:

- routine generation does not yet use the merged donor-synchronization engine;
- the validated 19-section premium report is not the routine package authority;
- current package readiness, guarded send and receipt closeout are not yet bound to the converged outputs;
- the system is not yet fully operational end to end.

## Objective

Promote the converged report engine into the routine production path and complete one fresh, guarded, receipt-confirmed Weekly ETF EU run.

The run must:

- use a fresh run ID, report date and suffix;
- use the latest accepted Weekly ETF donor state;
- refresh EU pricing and macro evidence to the latest feasible completed session;
- review every official position and every current promoted opportunity;
- deploy capital only where all current evidence and authority gates pass;
- retain blocked capacity as cash;
- generate Dutch-primary and English-companion premium HTML/PDF;
- validate the actual package visually and mechanically;
- send only an exact authorized package;
- confirm receipt independently before closeout.

## Four-layer scope

### 1. Decision framework

- Review all official positions: VWCE, EUNA and SXR8.
- Review all six current promoted donor opportunities.
- Preserve the frozen VVSM/L0CK review history without treating VVSM as currently promoted.
- Require explicit current action and zero-delta/no-trade results where applicable.
- Allow portfolio mutation only through a separate exact validated decision and state-write contract.
- Preserve official cash when no candidate passes every current gate.

### 2. Input/state contract

Authoritative inputs:

```text
official_portfolio=output/etf_eu_portfolio_state.json
official_trade_ledger=output/etf_eu_trade_ledger.csv
official_valuation_history=output/etf_eu_valuation_history.csv
latest_accepted_donor_commit=resolved_per_run
latest_completed_eu_session=resolved_per_run
ucits_registry=merged_isin_first_registry
wp09_stage_1_evidence=accepted_receipt
wp10_report_engine=merged_main_capability
```

Rules:

- previous report prose is not current authority;
- issuer NAV is not an exact exchange close;
- mapping completeness is not funding authority;
- analytical allocator weights are not actionable targets;
- no stale queue, manifest or delivery receipt may authorize the current run;
- every artifact must be bound to the exact run ID and source SHA.

### 3. Output contract

Required fresh package:

```text
Dutch primary HTML
Dutch primary PDF
English companion HTML
English companion PDF
production convergence state
pricing evidence
macro/donor lineage
mapping and allocation review
machine validation
visual review evidence
package readiness manifest
delivery result manifest
independent inbox receipt
routine closeout manifest
```

Client output requirements:

- premium 19-section hierarchy;
- official positions and cash reconcile exactly;
- current promoted opportunities are six-of-six mapped;
- frozen Stage-1 continuity is clearly separated;
- no development terminology or raw machine tokens;
- no stale simulated trades;
- receiving-mail HTML and PDFs tell the same action story;
- no delivery claim without a real receipt.

### 4. Operational runbook

1. Resolve the latest accepted donor commit and latest completed EU session.
2. Build fresh pricing and macro inputs.
3. Rebuild synchronized strategy, mappings and allocator context.
4. Build the converged routine state and bilingual report package.
5. Run complete machine and visual validation.
6. Build a run-scoped readiness manifest.
7. Create a guarded send authorization bound to exact file hashes and source SHA.
8. Send the exact package through the established delivery layer.
9. Perform delayed independent Gmail receipt verification.
10. Persist redacted receipt evidence, routine manifest and closeout.
11. Update current state, next actions, changelog, decision record and handover.

## Initial authority boundary

```text
portfolio_mutation=false
ledger_write=false
funding_authority=false
execution_authority=false
activation_authority=false
production_delivery_authority=false
```

Delivery authority may become true only inside a run-scoped guarded package after machine and visual readiness pass. Portfolio mutation remains independently gated.

## Acceptance contract

```text
fresh_run_id=true
fresh_report_suffix=true
latest_accepted_donor_resolved=true
latest_completed_eu_session_resolved=true
current_position_review_count=3
current_promoted_exposure_count=6
mapped_promoted_exposure_count=6
unmapped_promoted_exposure_count=0
portfolio_and_ledger_hashes_protected=true
client_report_machine_valid=true
visual_review_passed=true
ready_for_controlled_delivery=true
guarded_send_bound_to_exact_package=true
smtp_transport_success=true
independent_receipt_confirmed=true
expected_attachment_count=4
routine_manifest_complete=true
closeout_manifest_complete=true
```

## Initial next actions

1. Inspect current routine generation, pricing and production-action implementations.
2. Replace the routine renderer contract with the merged convergence engine.
3. Build a fresh no-send package.
4. Repair all concrete machine or visual defects.
5. Bind and execute guarded delivery.
6. Verify receipt independently and close the run.
