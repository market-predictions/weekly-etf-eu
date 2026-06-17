# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP12E validation, then decide whether a readiness preflight refresh is needed.

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
- WP12C recipient allowlist contract, inactive/sample-only
- WP12D mail setup policy contract, sample-only/no-live-values

WP12E current status:

```text
implemented
focused local validation passed
sample-only receipt artifact committed
not workflow-integrated
not delivery proof
no real delivery receipt
delivery_attempted=false
delivery_success=false
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
pdf_generation=false
recipient_activation=false
mail_transport_enabled=false
ready_for_wp13=false
related full-repo regression validation pending before full closeout
```

WP12E files:

```text
control/ETF_EU_DELIVERY_RECEIPT_CONTRACT_V1.md
output/delivery/etf_eu_delivery_receipt_sample_20260617_000000.json
tools/validate_etf_eu_delivery_receipt.py
tests/test_etf_eu_delivery_receipt.py
```

WP12E focused validation already run:

```text
python -m pytest tests/test_etf_eu_delivery_receipt.py -q
22 passed

python tools/validate_etf_eu_delivery_receipt.py output/delivery/etf_eu_delivery_receipt_sample_20260617_000000.json
ETF_EU_DELIVERY_RECEIPT_SAMPLE_OK
```

Next immediate action:

```text
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
```

Only after these pass should WP12E be marked fully closed.

After WP12E closeout, recommended next package:

```text
WP12F — readiness preflight refresh after all three prerequisite contract paths exist
```

Standing next rules:

- keep delivery blocked until a real delivery receipt path is separately implemented, validated and explicitly authorized
- keep U.S. ETFs as research proxies only
- keep candidate enrichment and promotion behind explicit fundability and portfolio-decision gates
- keep Twelve Data as a separate source-policy path; do not treat it as valuation authority unless a later decision and validator-backed integration explicitly allow it
- keep WP11 PDF rendering as local/shadow artifacts only
- do not integrate PDF rendering into the workflow until a later explicit decision authorizes it
- do not start WP13 real delivery enablement until explicit authority exists

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
recipient_activation=false
real_recipients=false
mail_setup_active=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13=false
```
