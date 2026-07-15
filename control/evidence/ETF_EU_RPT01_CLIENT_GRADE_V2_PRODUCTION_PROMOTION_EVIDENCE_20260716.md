# ETF EU RPT01 — Client-grade v2 production-promotion evidence

## Status

```text
production_renderer=client_grade_v2
promotion_status=completed
production_action_performed=false
```

## Fresh current-date comparison

```text
run_id=20260715_213100
report_date=2026-07-15
report_suffix=260715
workflow_run_id=29455916014
artifact_id=8359334286
artifact_digest=sha256:1c93c5d27366f95d3c07287954cd9ce4209ec593738c1d78b483171d9f259de4
same_current_inputs_used=true
pricing_observations=10
pricing_unresolved=1
macro_source_report_date=2026-07-14
macro_fresh_for_report=true
legacy_dutch_pages=3
legacy_english_pages=3
v2_dutch_pages=6
v2_english_pages=6
strict_v2_validation_passed=true
promotion_recommended=true
blockers=[]
```

## Promoted package smoke

```text
smoke_run_id=20260715_224700
workflow_run_id=29456627922
artifact_id=8359605163
artifact_digest=sha256:97ae3d5788ff783d793ba1fd83789f070cfa07ffd3faf529de7867a7e0a12277
promoted_package_builder_passed=true
strict_client_grade_v2_validation_passed=true
routine_v2_machine_gate_adapter_passed=true
dutch_page_count=6
english_page_count=6
all_dutch_pages_visually_reviewed=true
all_english_pages_visually_reviewed=true
visual_review_passed=true
client_language_clean=true
no_clipping=true
no_overlap=true
tables_readable=true
unicode_correct=true
transport_attempted=false
portfolio_mutation=false
```

## Readiness-adapter verification

```text
readiness_run_id=20260715_225500
workflow_run_id=29457156167
artifact_id=8359792531
artifact_digest=sha256:0e6f5f9d6876e1cc72e72f8a2dfed9e31262e1a37f8d2dd7f771515b00243e8c
promoted_package_builder_passed=true
strict_v2_machine_gate_passed=true
visual_review_evidence_accepted=true
v2_readiness_adapter_passed=true
ready_for_controlled_delivery_contract_passed=true
production_action_performed=false
```

## Promoted path

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

## Authority result

```text
canonical_identity=isin_first
us_etfs_research_only=true
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

## Conclusion

The current-date comparison, promoted package smoke, complete visual review and readiness-adapter verification all passed. Client-grade v2 is approved and implemented as the routine Weekly ETF EU production renderer.
