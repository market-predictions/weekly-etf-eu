# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-06-17

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Current phase

```text
Phase 8 — production Dutch-first report surface verified; delivery remains blocked
```

## Verified evidence

WP1 shadow workflow proof:

```text
output/validation/etf_eu_pricing_surface_shadow_20260604_213059.json
```

WP4 main workflow proof:

```text
GitHub Actions run #34 on main: success
artifact commit: 373bffb74745047aa79f3109ae62afd79e03abe1
output/validation/etf_eu_shadow_validation_evidence_20260604_220814.json
```

WP5 production Dutch-first report surface proof:

```text
GitHub Actions run #36 on main: success
trigger commit: 6c7851de339259baa258687196fc3e3dd68bd56a
artifact commit: f3ad95bb4b94eab8be54ae80e0eefc2e00fce478
output/weekly_etf_eu_review_260605.md
output/weekly_etf_eu_review_nl_260605.md
output/fundability/ucits_fundability_gate_20260605_070115.json
output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json
```

WP9 delivery manifest operational integration proof:

```text
GitHub Actions run #37 on main: success
trigger commit: d31a1c82f157f82288f7bc548762ea3e783c9ced
artifact commit: 5ac94fb42b12e4a80aeb8b9a8a44d5006283215e
ETF_EU_RUN_ID: 20260605_074604
output/delivery/etf_eu_delivery_manifest_20260605_074604.json
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
3 passed
python tools/validate_etf_eu_delivery_manifest.py output/delivery/etf_eu_delivery_manifest_20260605_074604.json
ETF_EU_DELIVERY_MANIFEST_OK
```

WP9 status:

```text
completed as blocked delivery manifest operational integration
main workflow verified
manifest artifact committed
not real delivery
not PDF generation
not email delivery
not a delivery receipt
```

WP9 manifest status fields:

```text
schema_version=etf_eu_delivery_manifest_v1
status=blocked_design_only
delivery_enabled=false
receipt_status=not_created
funding_authority=false
portfolio_mutation=false
valuation_grade_promotion=false
candidate_promotion_to_fundable=false
pdf_generation=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

WP9 manifest references:

```text
output/weekly_etf_eu_review_nl_260605.md
output/weekly_etf_eu_review_260605.md
output/pricing/ucits_valuation_prices_20260605_074604.json
output/fundability/ucits_fundability_gate_20260605_074604.json
output/validation/etf_eu_shadow_validation_evidence_20260605_074604.json
```

WP10 run artifact bundle / evidence package proof:

```text
runtime/build_etf_eu_run_bundle.py
tools/validate_etf_eu_run_bundle.py
tests/test_etf_eu_run_bundle.py
output/runs/20260605_070115/etf_eu_run_bundle_manifest.json
python -m pytest tests/test_etf_eu_run_bundle.py -q
4 passed
```

WP10 status:

```text
completed as run artifact bundle / evidence package
not delivery
not PDF generation
not email delivery
not a delivery receipt
```

WP10 sample bundle references:

```text
output/weekly_etf_eu_review_nl_260605.md
output/weekly_etf_eu_review_260605.md
output/pricing/ucits_valuation_prices_20260605_070115.json
output/fundability/ucits_fundability_gate_20260605_070115.json
output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json
```

WP10 original sample bundle status fields:

```text
delivery_manifest_status=not_available
delivery_manifest_path_or_null=null
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
```

WP10B run bundle delivery-manifest reference extension proof:

```text
GitHub Actions run #38 on main: success
implementation commit: f4aae64f0a6d2fefaf73c48d47feed5ccd49a61d
trigger commit: 4ba6caa28412b12c35bf9e3f6a4fb04a7ec796a9
artifact commit: 66e19d5ab1860a663a729ddddb9ff92aad341a70
ETF_EU_RUN_ID: 20260616_221743
output/runs/20260616_221743/etf_eu_run_bundle_manifest.json
output/delivery/etf_eu_delivery_manifest_20260616_221743.json
python -m pytest tests/test_etf_eu_run_bundle.py -q
4 passed
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
3 passed
```

WP10B run bundle status fields:

```text
delivery_manifest_status=available
delivery_manifest_path_or_null=output/delivery/etf_eu_delivery_manifest_20260616_221743.json
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
```

WP10B delivery manifest status fields:

```text
schema_version=etf_eu_delivery_manifest_v1
status=blocked_design_only
delivery_enabled=false
receipt_status=not_created
funding_authority=false
portfolio_mutation=false
valuation_grade_promotion=false
candidate_promotion_to_fundable=false
pdf_generation=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

WP10B status:

```text
completed as run bundle delivery-manifest reference extension
main workflow verified
run bundle artifact committed
blocked delivery manifest artifact committed
not real delivery
not PDF generation
not email delivery
not a delivery receipt
```

WP11 shadow PDF design/test proof:

```text
control/ETF_EU_SHADOW_PDF_CONTRACT_V1.md
runtime/render_etf_eu_shadow_pdf.py
tools/validate_etf_eu_shadow_pdf.py
tests/test_etf_eu_shadow_pdf.py
python -m pytest tests/test_etf_eu_shadow_pdf.py -q
3 passed
```

WP11 status:

```text
completed as shadow PDF design/test path only
not workflow-integrated
not production delivery
not email delivery
not a delivery receipt
```

WP12 email delivery dry-run contract proof:

```text
control/ETF_EU_EMAIL_DRY_RUN_CONTRACT_V1.md
runtime/build_etf_eu_email_dry_run.py
tools/validate_etf_eu_email_dry_run.py
tests/test_etf_eu_email_dry_run.py
output/delivery/email_dry_run_20260605_000000.json
python -m pytest tests/test_etf_eu_email_dry_run.py -q
5 passed
```

WP12 status:

```text
completed as email delivery dry-run contract only
design-only blocked artifact
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
not workflow-integrated
not real delivery
```

WP12 sample artifact status fields:

```text
delivery_manifest_status=not_available
pdf_status=not_available
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

## Current workflow posture

The main EU bootstrap workflow now uses:

```text
pricing.build_ucits_valuation_prices_with_agreement
runtime.render_etf_eu_report_with_pricing_surface
runtime.etf_eu_fundability_surface
runtime.build_etf_eu_delivery_manifest
runtime.build_etf_eu_run_bundle
```

The workflow now:

```text
builds the WP6 fundability gate artifact
validates the fundability artifact
passes the fundability artifact into the report renderer
validates strict Dutch-first output for the current report pair
validates pricing surface in strict mode
validates fundability surface
builds and validates a blocked/design-only delivery manifest
builds and validates a run bundle manifest referencing the blocked delivery manifest
commits report, pricing, fundability, validation, delivery manifest and run bundle artifacts as evidence
```

WP9 added a blocked delivery manifest operational integration path. The manifest is evidence/control metadata only and is not real delivery.

WP10 added an operator-friendly run bundle manifest path. It is an evidence package only and is not delivery.

WP10B workflow-integrated the run bundle evidence package so it references the blocked WP9-style delivery manifest when available. This is still evidence/control metadata only and does not create delivery authority.

WP11 added a shadow-only PDF helper/validator/test path, but this path is not workflow-integrated.

WP12 added an email delivery dry-run contract/helper/validator/test path. It is metadata/control only and is not workflow-integrated real delivery.

## Verified report-surface content

The generated Dutch report includes:

```text
Productierapport-volwassenheid
Nederlandse hoofdrapportage
primaire clientrapportage
Engelse rapportage is companion/operator-facing
agreement-gate pricing evidence
fundability gate status
gate blockers
gate-level status
candidate_promotion=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
geen gefinancierde UCITS-posities
geen koopadvies
geen productielevering
geen delivery receipt
```

The generated English report remains companion/operator-facing and confirms the Dutch report is the primary client report.

## Pending items

1. Later operational send path only after a separate real receipt path exists and is explicitly authorized.
2. Future candidate promotion only after explicit fundability and portfolio-decision gates pass.
3. Twelve Data source path remains separate and is not workflow/authority integrated as valuation authority.
4. PDF workflow integration remains blocked until a later explicit decision authorizes it.
5. WP13 real delivery enablement remains blocked until recipient allowlist, SMTP/secrets policy and delivery receipt validator exist.

## Boundary rule

The authority boundaries from `control/DECISION_LOG.md` remain unchanged:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
run_bundle=evidence_package_only
pdf_generation=shadow_only for local/shadow artifacts only
workflow_integrated=false for PDF
send_attempted=false
no email delivery
no delivery receipt
```
