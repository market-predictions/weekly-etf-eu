# Weekly ETF EU Review OS — Next Actions

Current priority: post-WP5 delivery-gated operational maturity.

Completed:

- shadow workflow verification
- main EU workflow wrapper switch
- WP5 production Dutch-first report surface verification
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
- output/runs/20260605_070115/etf_eu_run_bundle_manifest.json
- focused WP10 test: `python -m pytest tests/test_etf_eu_run_bundle.py -q` = `4 passed`
- control/ETF_EU_SHADOW_PDF_CONTRACT_V1.md
- runtime/render_etf_eu_shadow_pdf.py
- tools/validate_etf_eu_shadow_pdf.py
- tests/test_etf_eu_shadow_pdf.py
- focused WP11 test: `python -m pytest tests/test_etf_eu_shadow_pdf.py -q` = `3 passed`

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

- keep delivery blocked until the delivery manifest/receipt path is operationally implemented and verified
- keep U.S. ETFs as research proxies only
- keep candidate enrichment and promotion behind explicit fundability and portfolio-decision gates
- keep Twelve Data as a separate source-policy path; do not treat it as valuation authority unless a later decision and validator-backed integration explicitly allow it
- after WP9 delivery manifest operational integration is complete, optionally extend WP10 bundles to reference `delivery_manifest_status=available` and `delivery_manifest_path_or_null=output/delivery/etf_eu_delivery_manifest_<run_id>.json`
- keep WP11 PDF rendering as local/shadow artifacts only
- do not integrate PDF rendering into the workflow until WP9 delivery manifest operational integration is complete and a later explicit decision authorizes it

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
