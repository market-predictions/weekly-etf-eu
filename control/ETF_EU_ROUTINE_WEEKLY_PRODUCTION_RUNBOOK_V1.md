# ETF EU Routine Weekly Production Runbook V1

Date: 2026-07-16  
Repository: `market-predictions/weekly-etf-eu`

This is the authoritative operational runbook for fresh pricing, active-position review, candidate verification, allocation decisions, funded-aware report generation, guarded production action, delayed receipt verification and closeout.

## Phase 1 — Session start and authority

1. Read `control/SYSTEM_INDEX.md`.
2. Read `control/CURRENT_STATE.md`.
3. Read `control/NEXT_ACTIONS.md`.
4. Inspect the closest `market-predictions/weekly-etf` implementation before changing EU machinery.
5. Keep `weekly-etf-eu` as EU/UCITS source of truth.
6. Create a new `run_id`, `report_date` and `report_suffix` for a report run.
7. Never reuse dated queue, manifest or delivery evidence as current-run authority.
8. Ordinary repricing, position review and candidate verification are routine operations, not new architecture packages.

## Phase 2 — Current inputs and normalized state

Required inputs:

```text
portfolio_state=output/etf_eu_portfolio_state.json
valuation_history=output/etf_eu_valuation_history.csv
recommendation_scorecard=output/etf_eu_recommendation_scorecard.csv
pricing_artifact=output/pricing/ucits_close_price_validation_basket_results_<run_id>.json
macro_pack=output/macro/etf_eu_macro_policy_pack_<run_id>.json
ucits_registry=config/ucits_symbol_registry.yml
canonical_identity=isin_plus_exact_trading_line
us_etfs_research_only=true
```

Rules:

1. Obtain current completed-close UCITS pricing evidence.
2. Validate fund identity and exact trading line through the registry.
3. Use current EU portfolio state as quantity and cash authority.
4. Append or replace the report-date valuation-history observation deterministically.
5. Adapt current donor macro context with provenance; reject evidence more than three days older than the report date.
6. Treat previous reports as historical strategy context only.
7. Do not substitute issuer NAV for an exchange close.
8. Do not infer broker-account product permission from general venue support.
9. Do not fund or promote an ETF without required pricing, identity, investability and explicit allocation evidence.
10. Build one normalized run-scoped report state.

## Phase 3 — Active-position review

Every funded position must receive one canonical action:

```text
hold
hold_with_override
add_from_cash
reduce
replace_partial
replace_full
close
```

The review must determine:

```text
current market value
unrealized P&L
portfolio contribution
current weight
role validity
thesis status
relative-strength status
action_code
reason_codes
target_weight
trade_intent or explicit no-trade result
```

Rules:

1. Portfolio state is incumbent quantity authority.
2. A stale or unavailable exact-line close must be disclosed; do not invent a price.
3. A fresh-cash add requires fresh exact-line pricing, sufficient confirming evidence, concentration review and a new allocation decision.
4. No automatic second tranche is allowed.
5. Prose cannot create a trade. Only explicit validated `trade_intents[]` may support a guarded mutation.
6. If evidence is insufficient, use a governed hold/defer result and retain capital as cash.

## Phase 4 — Candidate verification and allocation review

For every candidate considered for capital, require:

```text
ISIN
UCITS status
PRIIPs/KID status
exact venue
exchange ticker
provider/Bloomberg/RIC identifiers where relevant
trading currency
fresh completed close
broker account-level product permission
portfolio overlap and concentration review
whole-share sizing
separate allocation decision
```

Identifier rules:

1. Ticker alone is never canonical authority.
2. Different share classes may not share one ISIN record.
3. Issuer exchange ticker and data-vendor/broker identifier must be stored separately when they differ.
4. Blocked target capacity remains cash and may not be silently reallocated.
5. The allocation artifact must expose `incumbent_reviews[]`, `candidate_reviews[]`, `trade_intents[]`, reason codes and authority fields.

## Phase 5 — Funded-aware client-grade v2 generation

The production renderer is:

```text
runtime/render_etf_eu_client_grade_v2_funded.py
```

The report builder is:

```text
tools/build_etf_eu_routine_report_package_v2.py
```

Generate Dutch-primary and English-companion outputs from the same normalized state.

Required hierarchy:

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

1. Use component-based HTML and WeasyPrint PDF generation.
2. Run the bilingual polish layer after rendering.
3. Keep internal authority fields outside client output.
4. Preserve U.S. ETFs as research-only references.
5. Preserve ISIN plus exact trading-line evidence.
6. Render funded positions, contribution and valuation history truthfully.
7. The normalized JSON state is the render authority; previous PDF prose is not an input.

## Phase 6 — Portfolio development and equity surface

1. Reconcile the latest history NAV to portfolio state.
2. Show the equity curve when meaningful validated history exists or a funded position exists.
3. Show a cash-preservation surface only while the portfolio is fully cash and history is flat.
4. Never publish a decorative or unreconciled graph.
5. A flat contribution caused by retention of the latest valid close must be explicitly described.

## Phase 7 — Machine and visual validation

Run:

```text
tools/validate_etf_eu_client_grade_report_v2.py
tools/write_etf_eu_routine_v2_machine_gate.py
tools/prepare_etf_eu_routine_package_readiness_v2.py
```

Required machine proof:

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
no_raw_markdown_leakage=true
page_count_between_6_and_14=true
```

Render all Dutch and English pages for review. Confirm:

```text
no clipping
no overlap
readable tables
correct Unicode
natural Dutch and English
correct investor/analyst hierarchy
no internal metadata
truthful position and equity surfaces
visual_review_passed=true
blockers=[]
```

Concrete copy or layout defects are repaired directly; do not create an architecture package.

## Phase 8 — Package readiness

1. Create the current-run package manifest.
2. Record state, pricing, macro, registry and renderer paths.
3. Require the strict machine gate and complete visual review.
4. Require current pricing coverage and date freshness.
5. Keep production-action authority false until a specific guarded run authorizes it.
6. Reject stale paths, superseded packages and reused identities.

Required fields include:

```text
client_renderer_mode=client_grade_v2_funded_aware
production_renderer=runtime/render_etf_eu_client_grade_v2_funded.py
normalized_report_state=<run-scoped path>
macro_policy_pack=<run-scoped path>
client_output_valid=true
ready_for_controlled_delivery=true
```

## Phase 9 — Existing production-action layer

The established production-action implementation remains authoritative for:

- run-specific authority;
- package selection;
- transport result;
- redacted evidence;
- receipt verification;
- final closeout.

Successful rendering or allocation review is not delivery. No real broker execution is performed by the report workflow.

## Phase 10 — Delayed receipt verification

After an explicitly authorized successful production action:

1. wait approximately ten minutes;
2. search the connected receipt mailbox/API for the matching run;
3. match date/run evidence and four expected attachments;
4. confirm Dutch PDF, English PDF, Dutch HTML and English HTML;
5. store only redacted metadata, hashes, timestamps and booleans;
6. keep `receipt_confirmed=false` when independent evidence is absent;
7. reconcile an existing receipt rather than sending a duplicate.

## Phase 11 — Closeout

1. Update the routine manifest.
2. Create the production closeout manifest.
3. Require valid client output, production result and independent receipt for delivery closeout.
4. Record blockers explicitly.
5. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`.
6. Record stable identifier, allocation or authority decisions in a decision artifact and, where practical, `control/DECISION_LOG.md`.
7. Never claim completed delivery without client-output, result and receipt evidence.

## Failure routing

```text
pricing failure -> repair current pricing run
fresh exact-line close unavailable -> disclose and block new allocation
broker permission unknown -> block candidate funding
identity conflict -> repair registry and basket before allocation
macro donor too old -> refresh donor evidence
valuation-history mismatch -> repair current observation
normalized state invalid -> repair state-builder input
machine failure -> repair concrete report defect
visual defect -> repair and repeat complete review
readiness failure -> repair package references or authority separation
production-action failure -> investigate current run
successful action but no receipt -> delayed independent recheck
existing valid receipt found -> reconcile; do not repeat action
valid output + successful action + confirmed receipt -> closeout
```

## Routine completion definition

A full delivered weekly run is complete only when:

```text
fresh current-run pricing exists
active positions were reviewed
candidate allocation decision exists
current macro provenance exists
valuation history contains the report-date observation
normalized funded-aware report state is valid
Dutch and English outputs exist
strict machine gate passed
complete visual review passed
package readiness passed
current-run production result exists
independent receipt evidence exists
receipt_confirmed=true
routine manifest updated
closeout manifest created
```

A no-trade allocation review may close independently of report delivery when its evidence, state and control files are complete and no delivery was requested.
