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

## Core authority boundary

The EU system remains delivery-gated and non-mutating.

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
send_attempted=false
email_delivery=false
delivery_receipt=false
pdf_generation=false for production workflow
recipient_activation=false
real_recipients=false
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13=false
```

## Verified evidence summary

WP1, WP4, WP5, WP9, WP10, WP10B, WP11, WP12, WP12B and WP12C remain verified/closed according to prior control-state evidence.

Key current closed delivery-gating packages:

```text
WP9   — blocked delivery manifest operational integration
WP10  — run artifact bundle / evidence package
WP10B — run bundle delivery-manifest reference extension
WP11  — shadow PDF rendering design/tests only
WP12  — email delivery dry-run contract only
WP12B — delivery readiness preflight contract
WP12C — recipient allowlist contract, inactive/sample-only
```

WP12C status remains:

```text
completed as recipient allowlist contract, inactive/sample-only
sample allowlist path=config/etf_eu_recipient_allowlist.sample.yml
recipient_activation=false
real_recipients=false
all_recipients_active=false
all_recipients_delivery_enabled=false
all_recipient_emails_placeholder_domain=example.invalid
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
pdf_generation=false
funding_authority=false
portfolio_mutation=false
candidate_promotion=false
valuation_grade_promotion=false
ready_for_wp13=false
not workflow-integrated
not real delivery
```

## WP12D SMTP/secrets policy status

WP12D implementation files are now present:

```text
control/ETF_EU_SMTP_SECRETS_POLICY_CONTRACT_V1.md
config/etf_eu_smtp_secrets_policy.sample.yml
tools/validate_etf_eu_smtp_secrets_policy.py
tests/test_etf_eu_smtp_secrets_policy.py
```

WP12D focused local validation:

```text
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
30 passed
```

WP12D sample policy status fields:

```text
schema_version=etf_eu_smtp_secrets_policy_v1
status=sample_only_no_secrets
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
send_attempted=false
email_delivery=false
production_delivery=false
delivery_receipt=false
smtp_host=placeholder.invalid
smtp_port=0
smtp_username=placeholder_only
smtp_secret_reference=placeholder_only
provider=placeholder_only
active=false
delivery_enabled=false
```

WP12D current status:

```text
implemented
focused local validation passed
sample no-secrets SMTP policy committed
not workflow-integrated
no real SMTP hostnames
no real credentials
no secrets in repo
not real delivery
not PDF generation
not email delivery
not a delivery receipt
ready_for_wp13=false
related regression commands still need to be run from a full repo checkout before marking WP12D fully closed
```

Required related regression commands still pending for WP12D closeout:

```text
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
python tools/validate_etf_eu_smtp_secrets_policy.py config/etf_eu_smtp_secrets_policy.sample.yml
```

## Current workflow posture

The main EU bootstrap workflow currently uses:

```text
pricing.build_ucits_valuation_prices_with_agreement
runtime.render_etf_eu_report_with_pricing_surface
runtime.etf_eu_fundability_surface
runtime.build_etf_eu_delivery_manifest
runtime.build_etf_eu_run_bundle
```

The workflow builds and validates report/pricing/fundability/delivery-manifest/run-bundle evidence only. WP12B, WP12C and WP12D are intentionally not workflow-integrated.

## Pending items

1. Finish WP12D related regression validation before closing WP12D.
2. Delivery receipt validator remains missing.
3. Recipient allowlist contract exists only as inactive/sample-only; no real recipients and no activation authority exist.
4. SMTP/secrets policy exists only as sample-only/no-secrets; no SMTP/secrets authority exists.
5. WP13 real delivery enablement remains blocked until recipient allowlist activation, SMTP/secrets policy, delivery receipt validator and an explicit delivery authority decision exist.
6. Later operational send path only after a separate real receipt path exists and is explicitly authorized.
7. Future candidate promotion only after explicit fundability and portfolio-decision gates pass.
8. Twelve Data source path remains separate and is not workflow/authority integrated as valuation authority.
9. PDF workflow integration remains blocked until a later explicit decision authorizes it.

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
recipient_activation=false
real_recipients=false
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13=false
```
