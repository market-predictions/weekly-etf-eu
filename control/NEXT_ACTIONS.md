# Weekly ETF EU Review OS — Next Actions

Current priority: post-WP12B delivery-gated operational maturity.

Completed:

- shadow workflow verification
- main EU workflow wrapper switch
- WP5 production Dutch-first report surface verification
- WP9 delivery manifest operational integration
- WP10 run artifact bundle / evidence package
- WP10B run bundle delivery-manifest reference extension
- WP11 shadow PDF rendering design/tests only
- WP12 email delivery dry-run contract only
- WP12B delivery readiness preflight contract

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
- output/delivery/etf_eu_delivery_manifest_20260605_074604.json
- focused WP9 test: `python -m pytest tests/test_etf_eu_delivery_manifest.py -q` = `3 passed`
- output/runs/20260605_070115/etf_eu_run_bundle_manifest.json
- focused WP10 test: `python -m pytest tests/test_etf_eu_run_bundle.py -q` = `4 passed`
- WP10B implementation commit f4aae64f0a6d2fefaf73c48d47feed5ccd49a61d
- GitHub Actions run #38 on main: success
- WP10B trigger commit 4ba6caa28412b12c35bf9e3f6a4fb04a7ec796a9
- WP10B artifact commit 66e19d5ab1860a663a729ddddb9ff92aad341a70
- output/runs/20260616_221743/etf_eu_run_bundle_manifest.json
- output/delivery/etf_eu_delivery_manifest_20260616_221743.json
- WP10B run bundle fields: `delivery_manifest_status=available`, `delivery_manifest_path_or_null=output/delivery/etf_eu_delivery_manifest_20260616_221743.json`, `production_delivery=false`, `email_delivery=false`, `pdf_generation=false`, `delivery_receipt=false`
- WP10B delivery manifest authority fields: `funding_authority=false`, `portfolio_mutation=false`, `candidate_promotion_to_fundable=false`, `production_delivery=false`, `email_delivery=false`, `pdf_generation=false`, `delivery_receipt=false`
- control/ETF_EU_SHADOW_PDF_CONTRACT_V1.md
- runtime/render_etf_eu_shadow_pdf.py
- tools/validate_etf_eu_shadow_pdf.py
- tests/test_etf_eu_shadow_pdf.py
- focused WP11 test: `python -m pytest tests/test_etf_eu_shadow_pdf.py -q` = `3 passed`
- output/delivery/email_dry_run_20260605_000000.json
- focused WP12 test: `python -m pytest tests/test_etf_eu_email_dry_run.py -q` = `5 passed`
- control/ETF_EU_DELIVERY_READINESS_PREFLIGHT_CONTRACT_V1.md
- runtime/build_etf_eu_delivery_readiness_preflight.py
- tools/validate_etf_eu_delivery_readiness_preflight.py
- tests/test_etf_eu_delivery_readiness_preflight.py
- output/delivery/etf_eu_delivery_readiness_preflight_20260617_000000.json
- focused WP12B test: `python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q` = `15 passed`
- related WP12B regression checks: `python -m pytest tests/test_etf_eu_email_dry_run.py -q` = `5 passed`; `python -m pytest tests/test_etf_eu_delivery_manifest.py -q` = `3 passed`; `python -m pytest tests/test_etf_eu_run_bundle.py -q` = `4 passed`
- direct WP12B sample validation: `python tools/validate_etf_eu_delivery_readiness_preflight.py output/delivery/etf_eu_delivery_readiness_preflight_20260617_000000.json` = `ETF_EU_DELIVERY_READINESS_PREFLIGHT_OK`

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

WP10B status:

```text
completed as run bundle delivery-manifest reference extension
main workflow verified
run bundle artifact committed
delivery_manifest_status=available
delivery_manifest_path_or_null=output/delivery/etf_eu_delivery_manifest_20260616_221743.json
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
not real delivery
not PDF generation
not email delivery
not a delivery receipt
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

WP12B status:

```text
completed as delivery readiness preflight contract
design-only blocked artifact
ready_for_wp13=false
recipient_allowlist_status=missing
smtp_secrets_policy_status=missing
delivery_receipt_validator_status=missing
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
pdf_generation=false
funding_authority=false
portfolio_mutation=false
candidate_promotion=false
valuation_grade_promotion=false
not workflow-integrated
not real delivery
```

Next:

- keep delivery blocked until a real delivery receipt path is separately implemented, validated and explicitly authorized
- keep U.S. ETFs as research proxies only
- keep candidate enrichment and promotion behind explicit fundability and portfolio-decision gates
- keep Twelve Data as a separate source-policy path; do not treat it as valuation authority unless a later decision and validator-backed integration explicitly allow it
- keep WP11 PDF rendering as local/shadow artifacts only
- do not integrate PDF rendering into the workflow until a later explicit decision authorizes it
- do not start WP13 real delivery enablement until recipient allowlist, SMTP/secrets policy and delivery receipt validator exist

Recommended next preparatory packages before WP13:

1. recipient allowlist contract, inactive/sample-only
2. SMTP/secrets policy contract, documentation-only/no secrets
3. delivery receipt validator contract, sample-only/no real delivery receipt

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
send_attempted=false
no email delivery
no delivery receipt
ready_for_wp13=false
```
