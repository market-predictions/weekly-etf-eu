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
client_output_valid=false
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

## Implementation status

```text
renderer_repair_implemented=true
machine_validator_created=true
rendered_page_review_helper_created=true
no_send_repair_workflow_created=true
normal_routine_workflow_hardened=true
repair_preview_generated=false
visual_review_passed=false
corrected_resend_executed=false
```

The repair preview must use the already committed Dutch and English Markdown files. Pricing, recommendations and portfolio state are not changed.

## Authority boundaries

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
receipt_confirmed=false
```

No resend and no receipt check are permitted in FIX1.

## Next action

```text
RUN_CLIENT_GRADE_PDF_REPAIR_PREVIEW
```

After the workflow persists the corrected HTML/PDF files and first/middle/last page renders, complete explicit visual review. Only a separately authorized corrected-resend package may follow a passed machine and visual gate.
