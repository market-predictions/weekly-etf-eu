# ETF EU Corrected Resend Contract V1

Date: 2026-07-13  
Repository: `market-predictions/weekly-etf-eu`

## Purpose

This contract governs a single corrected resend for the Weekly ETF EU report dated `2026-07-12` after the original SMTP transport succeeded but the original PDF attachments failed the client output contract.

## Four-layer separation

### Decision framework

The report recommendation is immutable for this correction:

```text
portfolio_action=no_transaction
cash_eur=100000
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

### Input/state contract

Correction authority consists only of:

```text
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_nl_260712.pdf
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.html
output/repair_preview/20260712_200000/weekly_etf_eu_review_260712.pdf
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000_nl.json
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000_en.json
output/quality/etf_eu_routine_pdf_client_grade_20260712_200000.json
output/quality/etf_eu_routine_pdf_visual_review_20260712_200000.json
```

The malformed original PDFs are historical defect evidence and are forbidden as correction attachments.

### Output contract

The correction package must:

- copy the four approved files byte-for-byte;
- use correction-labelled filenames;
- record source and delivery SHA-256 values;
- require source/delivery byte identity;
- preserve the original report date and analysis;
- create separate correction transport and delivery evidence;
- preserve the original transport evidence unchanged.

### Operational runbook

```text
approved repair-preview files
→ immutable correction package
→ package and queue validation
→ validate-only
→ dry-run
→ explicit guarded corrected resend
→ redacted correction evidence
→ delayed independent receipt verification
→ correction closeout
```

## Eligibility

```text
corrected_preview_generated=true
corrected_pdf_machine_gate_passed=true
corrected_pdf_visual_gate_passed=true
corrected_client_output_valid=true
machine_gate_blockers=[]
visual_review_blockers=[]
original_transport_success=true
original_client_output_valid=false
corrected_resend_executed=false
```

## Guarded-send rule

Live correction transport is allowed only when the workflow receives both:

```text
delivery_mode=send
send_confirmation=confirm_corrected_resend
```

Preparation, validate-only and dry-run are not live-send authority.

## Recipient and secret policy

```text
recipient_data_policy=redacted_hash_only
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_email_content_stored=false
raw_receipt_pdf_stored_in_github=false
```

SMTP secrets may exist only in the guarded send step. Raw subjects, bodies, recipient addresses and MIME messages must not be committed.

## Evidence filenames

```text
output/delivery/etf_eu_corrected_transport_result_<runtime_run_id>.json
output/delivery/etf_eu_corrected_delivery_evidence_<runtime_run_id>.json
output/delivery_authorization/etf_eu_corrected_resend_authorization_<runtime_run_id>.json
```

## Transport versus receipt

```text
smtp_sendmail_returned_no_exception=transport success only
receipt_confirmed=false after SMTP success
```

Independent delayed receipt verification is mandatory. A missing receipt must route to delayed recheck, not automatic resend.

## Failure routing

```text
package or hash failure → repair package; do not send
machine or visual gate failure → repair output; do not send
dry-run failure → repair workflow/runtime; do not send
SMTP failure → investigate transport; do not resend automatically
SMTP success without receipt → delayed independent receipt verification
confirmed corrected receipt → correction closeout and return to routine production
```

## Upstream donor decision

`market-predictions/weekly-etf` supplied the mature concepts for explicit report-path delivery, pre-send rendered-output validation, redacted recipient manifests, transport-versus-receipt separation and final run-manifest closeout. U.S. portfolio state, holdings, recipient authority, report discovery and delivery authority are not EU authority.
