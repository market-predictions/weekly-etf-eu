# ETF EU RPT01 — Client-grade v2 production promotion decision

## Decision date

2026-07-16

## Decision

Promote the client-grade v2 report architecture to the routine Weekly ETF EU production path.

The routine workflow now uses:

```text
current EU portfolio state
+ refreshed EU valuation history
+ fresh UCITS pricing evidence
+ current weekly-etf donor macro context adapted for EU descriptive use
+ normalized ETF EU report state
→ Dutch investor brief + analyst appendix
→ English investor brief + analyst appendix
→ strict client-grade v2 validation
→ complete rendered-page review evidence
→ existing readiness, guarded transport and receipt layers
```

The legacy three-page client surface is no longer the routine production renderer.

## Donor and authority rule

```text
source_of_truth_repo=market-predictions/weekly-etf-eu
reference_architecture_repo=market-predictions/weekly-etf
```

Adapted from `weekly-etf`:

- normalized runtime report state;
- investor/analyst hierarchy;
- component-based client renderer;
- macro and policy surface;
- structural opportunity radar;
- allocation map and second-order effects;
- conditional equity curve;
- strict client-surface validation.

Not copied from `weekly-etf`:

- U.S. holdings or portfolio state;
- U.S. ticker authority;
- U.S. recipient or delivery authority;
- U.S. funding or valuation authority.

EU authority remains:

```text
canonical_identity=isin_first
us_etfs_research_only=true
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

## Fresh current-date comparison evidence

Comparison identity:

```text
run_id=20260715_213100
report_date=2026-07-15
report_suffix=260715
```

Fresh inputs:

- current UCITS pricing: 10 priced lines, 1 unresolved line;
- donor macro pack dated 2026-07-14, adapted for the EU report date;
- current EU portfolio state;
- refreshed valuation-history observation;
- current UCITS registry.

Final comparison:

```text
workflow_run_id=29455916014
artifact_id=8359334286
artifact_digest=sha256:1c93c5d27366f95d3c07287954cd9ce4209ec593738c1d78b483171d9f259de4
same_current_inputs_used=true
strict_v2_validation_passed=true
macro_fresh_for_report=true
pricing_threshold_passed=true
promotion_recommended=true
blockers=[]
```

The current production-format report contained three pages per language. The v2 report contained six pages per language and added the investor/analyst hierarchy and the approved decision-support sections.

## Concrete defects repaired during the comparison

Only observed defects were repaired:

1. pricing calls below the repository throttle minimum are now clamped to the approved policy;
2. Dutch and English pricing-date headers were normalized;
3. Dutch `Core-aandelen` terminology was replaced with `Kernaandelen`;
4. Python validators are invoked as modules where package imports are required;
5. the comparison contract now relies on the authoritative strict validator for ISIN-first evidence rather than a fragile PDF word-count heuristic;
6. Dutch central-bank implications were localized;
7. fresh macro context is described as descriptive rather than historical;
8. preview-only footer wording was removed from production output.

## Promotion smoke evidence

Promotion smoke identity:

```text
smoke_run_id=20260715_224700
workflow_run_id=29456627922
artifact_id=8359605163
artifact_digest=sha256:97ae3d5788ff783d793ba1fd83789f070cfa07ffd3faf529de7867a7e0a12277
```

Results:

```text
promoted_package_builder_passed=true
strict_client_grade_v2_validation_passed=true
routine_v2_machine_gate_adapter_passed=true
dutch_page_count=6
english_page_count=6
all_dutch_pages_visually_reviewed=true
all_english_pages_visually_reviewed=true
visual_review_passed=true
transport_attempted=false
send_executed=false
portfolio_mutation=false
```

The current cash-only EU portfolio correctly shows a cash-preservation surface. The equity curve activates automatically only after meaningful validated NAV history or a funded position exists.

## Production implementation

Primary files:

```text
.github/workflows/run-weekly-etf-eu-routine.yml
tools/build_etf_eu_routine_report_package_v2.py
runtime/build_etf_eu_client_grade_report_state.py
runtime/render_etf_eu_client_grade_v2.py
runtime/polish_etf_eu_client_grade_html.py
runtime/adapt_weekly_etf_macro_for_eu.py
tools/update_etf_eu_valuation_history.py
tools/validate_etf_eu_client_grade_report_v2.py
tools/write_etf_eu_routine_v2_machine_gate.py
tools/prepare_etf_eu_routine_package_readiness_v2.py
```

The existing guarded delivery runner, redacted evidence layer and delayed independent receipt workflow remain unchanged.

## Operational consequence

The next normal Weekly ETF EU routine run automatically generates the client-grade v2 Dutch-primary and English-companion reports.

No separate shadow comparison, promotion workflow or user approval is required for each internal stage.

The normal visual review remains an output-quality check, not an architecture-development gate. Concrete defects may be repaired directly; a new architecture package is not required.

## Next action

```text
RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT_WITH_CLIENT_GRADE_V2
```
