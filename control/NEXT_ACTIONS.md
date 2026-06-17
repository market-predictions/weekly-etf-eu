# Weekly ETF EU Review OS — Next Actions

Current priority: decide whether WP13A delivery-authority review is appropriate.

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
- WP12F readiness preflight refresh after all three prerequisite paths exist

WP12F closeout status:

```text
completed
focused and related Codespace validation passed
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
```

WP12F validation evidence:

```text
preflight refresh validator: OK
readiness preflight tests: 15 passed
recipient allowlist tests: 22 passed
mail setup policy tests: 30 passed
delivery receipt tests: 22 passed
email dry-run tests: 5 passed
delivery manifest tests: 3 passed
```

Recommended next package:

```text
WP13A — explicit delivery-authority review decision, no send/no production delivery
```

WP13A should only decide whether delivery authority may be prepared. It must not send reports, enable production delivery, activate real recipients, generate production PDFs, or create a real delivery receipt.

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
