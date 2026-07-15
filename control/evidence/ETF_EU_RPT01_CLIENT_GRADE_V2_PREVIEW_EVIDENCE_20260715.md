# ETF EU RPT01 Client-Grade v2 Preview Evidence

Date: 2026-07-15

```text
workstream=ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2
preview_run_id=20260715_190000
source_run_id=20260712_125000
report_date=2026-07-12
report_suffix=260712
workflow_name=Weekly ETF EU client-grade v2 evidence
workflow_run_id=29442173869
workflow_conclusion=success
artifact_id=8353893752
artifact_name=etf-eu-client-grade-v2-evidence-20260715_190000
artifact_digest=sha256:a12ca45be8f13092afb2b6719afc68b4a6c54aed04c26cdda84de5a4645dcd44
artifact_expires_at=2026-10-13T18:50:28Z
client_grade_v2_passed=true
validation_blockers=0
dutch_page_count=6
english_page_count=6
dutch_visual_review_passed=true
english_visual_review_passed=true
all_pages_reviewed=true
no_clipping=true
no_overlap=true
unicode_valid=true
investor_analyst_hierarchy_passed=true
isin_first_visible=true
research_only_labelling_passed=true
equity_curve_contract_passed=true
current_equity_surface=cash_preservation_callout
macro_freshness_disclosure_passed=true
macro_refresh_required_before_production_promotion=true
portfolio_state_changed=false
production_delivery_performed=false
```

## Visual review

All six Dutch and six English pages were rendered locally from the workflow artifact and inspected.

The final polish corrected:

- Dutch masthead wrapping;
- dense opportunity-radar headers;
- dense pricing-table headers;
- untranslated Dutch next-run actions;
- the English bootstrap note on the Dutch surface;
- Dutch footer pagination;
- mixed wording for inverse and leveraged products.

The report contains an investor brief and an analyst appendix. Because the EU portfolio is still fully in cash and has only one validated NAV observation, the equity-curve contract correctly shows a cash-preservation callout instead of a meaningless flat graph. The SVG graph activates automatically after meaningful validated history exists.

## Remaining production boundary

The client-grade v2 architecture and preview are complete. Promotion into routine production requires one fresh routine-date shadow run with refreshed macro evidence and then one explicit renderer-promotion decision. The current production renderer and delivery workflow remain unchanged.
