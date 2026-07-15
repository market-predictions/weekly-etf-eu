# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-16

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Operating mode

```text
operating_mode=routine_production
production_renderer=client_grade_v2
client_grade_v2_promoted=true
routine_production_ready=true
selected_next_action=RUN_NEXT_ROUTINE_WEEKLY_ETF_EU_REPORT_WITH_CLIENT_GRADE_V2
```

## Latest completed delivery cycle

```text
work_package_id=ETF-EU-RUN260712-FIX2B_CORRECTED_RESEND_RECEIPT_CLOSEOUT
status=corrected_resend_receipt_confirmed_and_closed
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
correction_control_id=20260713_180000
repair_run_id=20260713_180000
transport_runtime_run_id=20260715_152543
github_workflow_run_id=29428021408
report_date=2026-07-12
report_suffix=260712
corrected_resend_executed=true
correction_transport_attempted=true
correction_transport_success=true
receipt_check_status=receipt_confirmed
receipt_confirmed=true
expected_attachment_set_seen=true
attachment_count_seen=4
production_delivery_complete=true
production_delivery_cycle_closed=true
additional_resend_required=false
```

## Client-grade v2 production promotion

```text
workstream=ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2
execution_mode=integrated_fast_track
status=promoted_to_routine_production
promotion_decision=control/decisions/ETF_EU_RPT01_CLIENT_GRADE_V2_PRODUCTION_PROMOTION_DECISION_20260716.md
fresh_comparison_run_id=20260715_213100
fresh_comparison_report_date=2026-07-15
fresh_comparison_report_suffix=260715
fresh_comparison_workflow_run_id=29455916014
fresh_comparison_artifact_id=8359334286
fresh_comparison_artifact_digest=sha256:1c93c5d27366f95d3c07287954cd9ce4209ec593738c1d78b483171d9f259de4
same_current_inputs_used=true
strict_v2_validation_passed=true
comparison_blocker_count=0
promotion_recommended=true
promotion_applied=true
```

## Production-promotion smoke evidence

```text
smoke_run_id=20260715_224700
smoke_workflow_run_id=29456627922
smoke_artifact_id=8359605163
smoke_artifact_digest=sha256:97ae3d5788ff783d793ba1fd83789f070cfa07ffd3faf529de7867a7e0a12277
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

## Promoted routine report architecture

```text
fresh UCITS pricing
+ current EU portfolio state
+ refreshed EU valuation history
+ current donor macro context adapted for EU descriptive use
+ UCITS registry
→ normalized ETF EU report state
→ Dutch investor brief + analyst appendix
→ English investor brief + analyst appendix
→ strict client-grade v2 machine contract
→ complete page-review evidence
→ existing readiness contract
→ existing guarded transport and receipt layers
```

Implemented capabilities:

```text
investor_brief_present=true
analyst_appendix_present=true
report_section_count=15
macro_and_policy_surface_implemented=true
opportunity_radar_implemented=true
risk_and_invalidation_surface_implemented=true
allocation_map_implemented=true
second_order_effects_implemented=true
verification_funnel_implemented=true
conditional_position_sections_implemented=true
valuation_history_updater_implemented=true
equity_curve_svg_contract_implemented=true
current_equity_surface=cash_preservation_callout
equity_curve_activation=automatic_after_meaningful_validated_history
```

Primary production files:

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

## Authority and privacy boundaries

```text
canonical_identity=isin_first
us_etfs_research_only=true
portfolio_action=no_transaction
cash_eur=100000
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
raw_mailbox_headers_stored=false
raw_receipt_pdf_stored_in_github=false
weekly_etf_eu_source_of_truth=true
weekly_etf_upstream_donor_only=true
```

## Delivery boundary

The promotion comparison and smoke run performed no transport and sent no email. Future routine sends continue to require the existing explicit guarded-send authority, client-output quality evidence and independent receipt closeout.

## Current note

The six development phases are complete and the client-grade v2 renderer is now the routine production renderer. The next fresh Weekly ETF EU report must use a new run identity, current pricing and macro evidence, and will automatically generate the premium Dutch-primary and English-companion reports. No further shadow-comparison or architecture approval cycle is required unless a concrete defect is observed.
