# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP12D validation, then continue delivery-gated operational maturity.

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

WP12D current status:

```text
implemented
focused local validation passed
sample no-secrets SMTP policy committed
not workflow-integrated
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
ready_for_wp13=false
related regression validation pending before full closeout
```

WP12D files:

```text
control/ETF_EU_SMTP_SECRETS_POLICY_CONTRACT_V1.md
config/etf_eu_smtp_secrets_policy.sample.yml
tools/validate_etf_eu_smtp_secrets_policy.py
tests/test_etf_eu_smtp_secrets_policy.py
```

WP12D focused validation already run:

```text
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
30 passed
```

Next immediate action:

```text
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
python tools/validate_etf_eu_smtp_secrets_policy.py config/etf_eu_smtp_secrets_policy.sample.yml
```

Only after these pass should WP12D be marked fully closed.

After WP12D closeout, recommended next preparatory package before WP13:

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
- do not start WP13 real delivery enablement until recipient allowlist activation, SMTP/secrets policy, delivery receipt validator and explicit authority exist

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
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13=false
```
