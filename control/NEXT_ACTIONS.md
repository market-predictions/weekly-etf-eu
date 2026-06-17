# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP12F validation, then decide whether WP13 delivery-authority review is appropriate.

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
- WP12E delivery receipt validator contract, sample-only/no real delivery receipt

WP12F current status:

```text
implemented
refreshed readiness preflight artifact committed
status=ready_for_wp13_preflight_only
ready_for_wp13=true
all three prerequisite contract paths present
real delivery not authorized remains present
not workflow-integrated
not delivery authority
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
pdf_generation=false
funding_authority=false
portfolio_mutation=false
candidate_promotion=false
valuation_grade_promotion=false
related Codespace validation pending before full closeout
```

WP12F artifact:

```text
output/delivery/etf_eu_delivery_readiness_preflight_20260617_000001.json
```

Next immediate action:

```text
python tools/validate_etf_eu_delivery_readiness_preflight.py output/delivery/etf_eu_delivery_readiness_preflight_20260617_000001.json
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
python -m pytest tests/test_etf_eu_delivery_receipt.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
```

Only after these pass should WP12F be marked fully closed.

After WP12F closeout, next likely package:

```text
WP13A — explicit delivery-authority review decision, no send/no production delivery
```

WP13A should decide whether delivery authority may be prepared, but it should not send reports or enable production delivery unless a later package explicitly does so.

Standing next rules:

- keep delivery blocked until a real delivery receipt path is separately implemented, validated and explicitly authorized
- keep U.S. ETFs as research proxies only
- keep candidate enrichment and promotion behind explicit fundability and portfolio-decision gates
- keep Twelve Data as a separate source-policy path; do not treat it as valuation authority unless a later decision and validator-backed integration explicitly allow it
- keep WP11 PDF rendering as local/shadow artifacts only
- do not integrate PDF rendering into the workflow until a later explicit decision authorizes it
- do not start any operational send package until explicit authority exists and is recorded

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
ready_for_wp13_preflight_only=true
wp13_delivery_authority=false
```
