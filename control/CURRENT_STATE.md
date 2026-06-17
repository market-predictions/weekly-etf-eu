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
mail_setup_active=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13=false
```

## Verified evidence summary

The following delivery-gating packages are now closed:

```text
WP9   — blocked delivery manifest operational integration
WP10  — run artifact bundle / evidence package
WP10B — run bundle delivery-manifest reference extension
WP11  — shadow PDF rendering design/tests only
WP12  — email delivery dry-run contract only
WP12B — delivery readiness preflight contract
WP12C — recipient allowlist contract, inactive/sample-only
WP12D — mail setup policy contract, sample-only/no-live-values
```

WP12C remains inactive/sample-only:

```text
sample allowlist path=config/etf_eu_recipient_allowlist.sample.yml
recipient_activation=false
real_recipients=false
all_recipients_active=false
all_recipients_delivery_enabled=false
all_recipient_emails_placeholder_domain=example.invalid
ready_for_wp13=false
not workflow-integrated
not real delivery
```

## WP12D status

WP12D implementation files are present and committed.

WP12D validation proof:

```text
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
30 passed

python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
15 passed

python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
22 passed

python -m pytest tests/test_etf_eu_email_dry_run.py -q
5 passed

python -m pytest tests/test_etf_eu_delivery_manifest.py -q
3 passed

mail setup policy validator
OK
```

WP12D current status:

```text
completed as mail setup policy contract, sample-only/no-live-values
contract/sample policy/validator/tests committed
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

1. Delivery receipt validator remains missing.
2. Recipient allowlist contract exists only as inactive/sample-only; no real recipients and no activation authority exist.
3. Mail setup policy exists only as sample-only/no-live-values; no mail-transport authority exists.
4. WP13 real delivery enablement remains blocked until recipient allowlist activation, mail setup policy, delivery receipt validator and an explicit delivery authority decision exist.
5. Later operational send path only after a separate real receipt path exists and is explicitly authorized.
6. Future candidate promotion only after explicit fundability and portfolio-decision gates pass.
7. Twelve Data source path remains separate and is not workflow/authority integrated as valuation authority.
8. PDF workflow integration remains blocked until a later explicit decision authorizes it.

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
mail_setup_active=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13=false
```
