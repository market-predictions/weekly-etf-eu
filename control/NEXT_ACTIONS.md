# Weekly ETF EU Review OS — Next Actions

Current priority: continue delivery-gated operational maturity after WP12D closeout.

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

WP12D closeout status:

```text
completed
focused and related Codespace validation passed
not workflow-integrated
mail_setup_active=false
mail_transport_enabled=false
external_mail_api_enabled=false
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
ready_for_wp13=false
```

WP12D validation evidence:

```text
focused WP12D test: 30 passed
readiness preflight tests: 15 passed
recipient allowlist tests: 22 passed
email dry-run tests: 5 passed
delivery manifest tests: 3 passed
mail setup policy validator: OK
```

Recommended next preparatory package before WP13:

```text
WP12E — delivery receipt validator contract, sample-only/no real delivery receipt
```

Standing next rules:

- keep delivery blocked until a real delivery receipt path is separately implemented, validated and explicitly authorized
- keep U.S. ETFs as research proxies only
- keep candidate enrichment and promotion behind explicit fundability and portfolio-decision gates
- keep Twelve Data as a separate source-policy path; do not treat it as valuation authority unless a later decision and validator-backed integration explicitly allow it
- keep WP11 PDF rendering as local/shadow artifacts only
- do not integrate PDF rendering into the workflow until a later explicit decision authorizes it
- do not start WP13 real delivery enablement until recipient allowlist activation, mail setup policy, delivery receipt validator and explicit authority exist

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
