# Weekly ETF EU Review OS — Next Actions

Current priority: post-WP5 delivery-gated operational maturity.

Completed:

- shadow workflow verification
- main EU workflow wrapper switch
- WP5 production Dutch-first report surface verification
- WP9 delivery manifest operational integration
- WP10 run artifact bundle / evidence package
- WP11 shadow PDF rendering design/tests only

Evidence:

- output/validation/etf_eu_pricing_surface_shadow_20260604_213059.json
- output/validation/etf_eu_shadow_validation_evidence_20260604_220814.json
- WP4 artifact commit 373bffb74745047aa79f3109ae62afd79e03abe1
- GitHub Actions run #36 on main: success
- WP5 trigger commit 6c7851de339259baa258687196fc3e3dd68bd56a
- WP5 artifact commit f3ad95bb4b94eab8be54ae80e0eefc2e00fce478
- output/weekly_etf_eu_review_260605.md
- output/weekly_etf_eu_review_nl_260605.md
- output/fundability/ucits_fundability_gate_20260605_070115.json
- output/validation/etf_eu_shadow_validation_evidence_20260605_070115.json
- GitHub Actions run #37 on main: success
- WP9 trigger commit d31a1c82f157f82288f7bc548762ea3e783c9ced
- WP9 artifact commit 5ac94fb42b12e4a80aeb8b9a8a44d5006283215e
- WP9 ETF_EU_RUN_ID 20260605_074604
- output/delivery/etf_eu_delivery_manifest_20260605_074604.json
- focused WP9 test: `python -m pytest tests/test_etf_eu_delivery_manifest.py -q` = `3 passed`
- direct WP9 manifest validation: `python tools/validate_etf_eu_delivery_manifest.py output/delivery/etf_eu_delivery_manifest_20260605_074604.json` = `ETF_EU_DELIVERY_MANIFEST_OK`
- output/runs/20260605_070115/etf_eu_run_bundle_manifest.json
- focused WP10 test: `python -m pytest tests/test_etf_eu_run_bundle.py -q` = `4 passed`
- control/ETF_EU_SHADOW_PDF_CONTRACT_V1.md
- runtime/render_etf_eu_shadow_pdf.py
- tools/validate_etf_eu_shadow_pdf.py
- tests/test_etf_eu_shadow_pdf.py
- focused WP11 test: `python -m pytest tests/test_etf_eu_shadow_pdf.py -q` = `3 passed`

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

WP10 status:

```text
completed as run artifact bundle / evidence package
not delivery
not PDF generation
not email delivery
not a delivery receipt
delivery_manifest_status=not_available
delivery_manifest_path_or_null=null
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
```

Next:

- keep delivery blocked until a real delivery receipt path is separately implemented, validated and explicitly authorized
- keep U.S. ETFs as research proxies only
- keep candidate enrichment and promotion behind explicit fundability and portfolio-decision gates
- keep Twelve Data as a separate source-policy path; do not treat it as valuation authority unless a later decision and validator-backed integration explicitly allow it
- optionally extend WP10 bundles to reference `delivery_manifest_status=available` and `delivery_manifest_path_or_null=output/delivery/etf_eu_delivery_manifest_<run_id>.json` while keeping WP10 as evidence package only
- keep WP11 PDF rendering as local/shadow artifacts only
- do not integrate PDF rendering into the workflow until a later explicit decision authorizes it
- do not start WP13 real delivery enablement until WP9, WP10, WP11 and WP12 are all verified and recipient allowlist, SMTP/secrets policy and delivery receipt validator exist

Boundary rule: existing decision-log boundaries remain unchanged.

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
