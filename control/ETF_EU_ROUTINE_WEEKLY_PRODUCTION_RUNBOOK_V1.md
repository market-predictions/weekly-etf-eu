# ETF EU Routine Weekly Production Runbook V1

Date: 2026-07-16  
Repository: `market-predictions/weekly-etf-eu`

This is the authoritative operational runbook for fresh generation, client-grade v2 validation, controlled production action, delayed receipt verification and closeout of routine Weekly ETF EU reports.

## Phase 1 — Session start and authority

1. Read `control/SYSTEM_INDEX.md`.
2. Read `control/CURRENT_STATE.md`.
3. Read `control/NEXT_ACTIONS.md`.
4. Inspect the closest `market-predictions/weekly-etf` implementation before changing EU machinery.
5. Keep `weekly-etf-eu` as EU/UCITS source of truth.
6. Create a new `run_id`, `report_date` and `report_suffix`.
7. Never reuse a previous run's dated queue, manifests or evidence as current-run authority.

## Phase 2 — Current inputs and normalized state

1. Obtain current UCITS pricing evidence.
2. Validate UCITS identity through the EU registry and ISIN-first rules.
3. Use current EU portfolio state as authority.
4. Append or replace the current report-date observation in EU valuation history.
5. Adapt the current `weekly-etf` macro-policy pack as descriptive EU context with provenance.
6. Reject donor macro evidence that is more than three days older than the EU report date.
7. Treat previous reports as historical strategy context only.
8. Do not fund or promote an ETF without required pricing, identity and investability evidence.
9. Build one normalized run-scoped ETF EU report state.

Required input/state contract:

```text
portfolio_state=output/etf_eu_portfolio_state.json
valuation_history=output/etf_eu_valuation_history.csv
pricing_artifact=output/pricing/ucits_close_price_validation_basket_results_<run_id>.json
macro_pack=output/macro/etf_eu_macro_policy_pack_<run_id>.json
ucits_registry=config/ucits_symbol_registry.yml
canonical_identity=isin_first
us_etfs_research_only=true
```

## Phase 3 — Client-grade v2 generation

The routine production renderer is:

```text
runtime/render_etf_eu_client_grade_v2.py
```

The report builder is:

```text
tools/build_etf_eu_routine_report_package_v2.py
```

The native output consists of two client surfaces in each language:

### Investor brief

1. Decision cockpit
2. Portfolio and capital
3. Regime and policy dashboard
4. Structural UCITS opportunity radar
5. Key risks and invalidations
6. Portfolio development
7. Conclusion

### Analyst appendix

8. Allocation map
9. Second-order effects
10. UCITS candidates and pricing evidence
11. Verification funnel
12. Current-position review
13. Replacement, rotation and avoidance radar
14. Input for the next run
15. Disclaimer

Rules:

1. Generate Dutch-primary and English-companion reports from the same normalized state.
2. Use component-based HTML and WeasyPrint PDF generation.
3. Run the narrow bilingual polish layer after rendering.
4. Keep internal authority and production-state fields outside client output.
5. Preserve U.S. ETFs as research references only.
6. Preserve ISIN-first identity and explicit trading-line evidence.
7. Keep the generated Markdown as a decision-summary audit companion; the normalized JSON report state is the authoritative v2 render source.
8. Never regenerate client prose from previous PDF text.

Required client hierarchy:

```text
investor_brief_present=true
analyst_appendix_present=true
report_section_count=15
client_renderer_mode=client_grade_v2
```

## Phase 4 — Portfolio development and equity surface

1. Update valuation history deterministically for the report date.
2. Reconcile the latest history NAV to current portfolio NAV.
3. Show the equity curve only when meaningful validated history exists or a funded position exists.
4. Show the cash-preservation surface while the portfolio is fully in cash and NAV history is flat.
5. Never publish a decorative flat graph merely to fill report space.

Current activation rule:

```text
show_equity_curve =
  at_least_two_meaningful_validated_NAV_observations
  OR funded_position_exists
```

## Phase 5 — Machine and visual validation

Run:

```text
tools/validate_etf_eu_client_grade_report_v2.py
tools/write_etf_eu_routine_v2_machine_gate.py
tools/prepare_etf_eu_routine_package_readiness_v2.py
```

The strict client-grade contract must prove:

```text
normalized_report_state_valid=true
all_15_required_sections_present=true
investor_analyst_hierarchy_passed=true
isin_first_visible=true
research_only_labelling_passed=true
macro_freshness_disclosure_passed=true
equity_curve_contract_passed=true
client_surface_clean=true
authority_metadata_absent=true
raw_status_enums_absent=true
internal_authority_fields_absent=true
no_raw_Markdown_leakage=true
page_count_between_6_and_14=true
```

Render all Dutch and English pages for review. First/middle/last-page extracts may remain as navigation aids, but the complete report must be available for visual inspection.

The visual review must confirm:

```text
no clipping
no overlap
readable tables
correct Unicode
natural Dutch and English
correct investor/analyst hierarchy
no internal metadata
truthful equity surface
visual_review_passed=true
blockers=[]
```

Ordinary wording or layout repairs may be made directly. Do not create a new architecture package for a concrete client-copy defect.

## Phase 6 — Package readiness

1. Create the current-run package manifest.
2. Record the normalized report-state path, macro pack, registry and renderer mode.
3. Require the strict v2 machine gate.
4. Require the rendered-page visual review.
5. Require current pricing coverage and date freshness.
6. Keep all authority fields false until the existing production-action layer authorizes the specific run.
7. Reject stale paths, superseded packages and reused identities.

Required package fields include:

```text
client_renderer_mode=client_grade_v2
production_renderer=runtime/render_etf_eu_client_grade_v2.py
normalized_report_state=<run-scoped path>
macro_policy_pack=<run-scoped path>
investor_brief_present=true
analyst_appendix_present=true
conditional_equity_curve_enabled=true
client_output_valid=true
ready_for_controlled_delivery=true
```

## Phase 7 — Existing production-action layer

The v2 promotion changes the client-generation and validation layers only.

The established production-action implementation remains authoritative for:

- run-specific authority;
- package selection;
- transport result;
- redacted evidence;
- receipt verification;
- final closeout.

Do not infer successful delivery from successful rendering or validation. A completed action still requires its own result and evidence.

## Phase 8 — Delayed receipt verification

Independent delayed receipt verification remains mandatory after successful production action.

1. Wait approximately 10 minutes.
2. Search the connected receipt mailbox/API for the matching current-run message.
3. Match run/date evidence and the expected four-file attachment set.
4. Confirm Dutch PDF, English PDF, Dutch HTML and English HTML.
5. Store only redacted metadata, hashes where available, timestamps and booleans.
6. Keep `receipt_confirmed=false` if independent evidence is not found.
7. Recheck later rather than creating an automatic duplicate.

### Existing-receipt reconciliation rule

If the expected message and attachment set have already been independently observed, reconcile the existing result and receipt. Do not perform another production action merely to improve evidence.

## Phase 9 — Closeout

1. Update the routine run manifest.
2. Create the production closeout manifest.
3. Require valid client output.
4. Require successful production result.
5. Require confirmed independent receipt for completed closeout.
6. Record blockers explicitly.
7. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`.
8. Never claim completed delivery without client-output, result and receipt evidence.

## Failure routing

```text
pricing failure -> repair current pricing run
macro donor too old -> refresh donor macro evidence
valuation-history mismatch -> repair current history observation
normalized state invalid -> repair state builder input
v2 machine failure -> repair concrete report defect
visual defect -> repair report and repeat complete page review
readiness failure -> repair package references or authority separation
production-action failure -> investigate the current run
successful action but no receipt -> delayed independent recheck
existing valid receipt found -> reconcile; do not repeat action
valid client output + successful action + confirmed receipt -> closeout
```

## Routine completion definition

A routine weekly run is complete only when:

```text
fresh current-run pricing exists
current macro provenance exists
valuation history contains the report-date observation
normalized v2 report state is valid
Dutch and English v2 outputs exist
strict v2 machine gate passed
complete visual review passed
package readiness passed
current-run production result exists
independent receipt evidence exists
receipt_confirmed=true
routine manifest updated
closeout manifest created
```

## Operating rule

Client-grade v2 is the routine production renderer. New architecture packages are created only for a material capability change. Normal weekly reports and concrete defect repairs are routine operations under this runbook.
