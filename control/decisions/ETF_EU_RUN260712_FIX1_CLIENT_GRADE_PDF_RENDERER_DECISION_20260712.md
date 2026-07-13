# ETF EU RUN260712 FIX1 — Client-grade PDF renderer decision

Date: 2026-07-12  
Repository: `market-predictions/weekly-etf-eu`

## Decision

The `2026-07-12` routine transport succeeded at the SMTP layer, but the transmitted Dutch and English PDFs failed the client output contract.

```text
source_run_id=20260712_125000
source_runtime_run_id=20260712_182002
transport_attempted=true
transport_success=true
receipt_confirmed=false
original_client_output_valid=false
production_delivery_complete=false
```

The defect was caused by the routine builder passing full Markdown to the legacy `_simple_pdf` Latin-1 plain-text renderer. PDF file validity did not prove content completeness or client-grade rendering.

## Upstream pattern adapted

Inspected in `market-predictions/weekly-etf`:

```text
send_report.py
send_report_OLD.py
send_report_runtime_html.py
tools/validate_etf_delivery_html_contract.py
tools/validate_etf_pdf_visual_contract.py
.github/workflows/send-weekly-report.yml
```

Adapted:

```text
Markdown preprocessing
Mistune table rendering
semantic HTML
WeasyPrint PDF generation
PDF-specific pagination CSS
Poppler text extraction
first/middle/last rendered-page review
pre-delivery client-output gating
```

Intentionally rejected:

```text
U.S. portfolio panels
U.S. holdings logic
TradingView authority
U.S. recipients and delivery authority
U.S. equity-curve-specific requirements
seventeen-section U.S. report structure
```

## Repair verification

GitHub Actions run:

```text
run_id=29246566901
job=repair-preview
conclusion=success
artifact_id=8277605032
repair_run_id=20260712_200000
```

Machine gate:

```text
dutch_pdf_client_grade_passed=true
english_pdf_client_grade_passed=true
pdf_client_grade_passed=true
dutch_page_count=3
english_page_count=3
pricing_lines_detected_nl=11
pricing_lines_detected_en=11
required_sections_present=true
section_8_present_near_end=true
semantic_tables_present=true
markdown_leakage_detected=false
unicode_integrity_passed=true
duplicate_title_detected=false
```

Visual review:

```text
first_page_reviewed=true
middle_page_reviewed=true
last_page_reviewed=true
no_right_edge_clipping=true
no_bottom_clipping=true
no_overlapping_text=true
tables_readable=true
headings_readable=true
unicode_correct=true
all_sections_visible=true
duplicate_title_absent=true
visual_review_passed=true
blockers=[]
```

## Implementation status

```text
renderer_repair_implemented=true
machine_validator_created=true
rendered_page_review_helper_created=true
no_send_repair_workflow_created=true
normal_routine_workflow_hardened=true
repair_preview_generated=true
machine_review_passed=true
visual_review_passed=true
corrected_resend_executed=false
```

The repair preview used the already committed Dutch and English Markdown files. Pricing, recommendations and portfolio state were not changed.

## Authority boundaries

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
receipt_confirmed=false
correction_transport_attempted=false
corrected_resend_executed=false
```

No resend and no receipt check occurred in FIX1.

## Next action

```text
PREPARE_EXPLICIT_CORRECTED_REPORT_RESEND
```

The corrected Dutch and English previews have passed both machine and visual review. A separate corrected-resend package may now be prepared, but no transport may be claimed until that separately authorized workflow produces current correction transport evidence.
