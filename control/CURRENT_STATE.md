# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-06-05

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
workflow integration not yet required
```

WP10 sample bundle references:

```text
output/weekly_etf_eu_review_nl_260605.md
output/weekly_etf_eu_review_260605.md
output/pricing/ucits_valuation_prices_20260605_070115.json
output/fundability/ucits_fundability_gate_20260605_070115.json
output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json
```

WP10 sample bundle status fields:

```text
delivery_manifest_status=not_available
delivery_manifest_path_or_null=null
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
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

## Current workflow posture

The main EU bootstrap workflow now uses:

```text
pricing.build_ucits_valuation_prices_with_agreement
runtime.render_etf_eu_report_with_pricing_surface
runtime.etf_eu_fundability_surface
```

The workflow now:

```text
builds the WP6 fundability gate artifact
validates the fundability artifact
passes the fundability artifact into the report renderer
validates strict Dutch-first output for the current report pair
validates pricing surface in strict mode
validates fundability surface
commits report, pricing, fundability and validation artifacts as evidence
```

WP10 added an operator-friendly run bundle manifest path. It is an evidence package only and is not workflow-integrated delivery.

WP11 added a shadow-only PDF helper/validator/test path, but this path is not workflow-integrated.

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

1. Later operational send path only after a separate manifest/receipt path exists.
2. Future candidate promotion only after explicit fundability and portfolio-decision gates pass.
3. Twelve Data source path remains separate and is not workflow/authority integrated as valuation authority.
4. PDF workflow integration remains blocked until WP9 delivery manifest operational integration is complete and a later explicit decision authorizes it.
5. After WP9 delivery manifest operational integration is complete, WP10 may be extended to reference an available delivery manifest while remaining an evidence package only.

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
no email delivery
no delivery receipt
```
