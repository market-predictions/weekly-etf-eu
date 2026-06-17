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
ready_for_wp13_preflight_only=true
wp13_delivery_authority=false
```

## Verified evidence summary

The following delivery-gating packages are closed:

```text
WP9   — blocked delivery manifest operational integration
WP10  — run artifact bundle / evidence package
WP10B — run bundle delivery-manifest reference extension
WP11  — shadow PDF rendering design/tests only
WP12  — email delivery dry-run contract only
WP12B — delivery readiness preflight contract
WP12C — recipient allowlist contract, inactive/sample-only
WP12D — mail setup policy contract, sample-only/no-live-values
WP12E — delivery receipt validator contract, sample-only/no real delivery receipt
WP12F — readiness preflight refresh after all three prerequisite paths exist
```

WP12F refreshed preflight artifact is present and committed:

```text
output/delivery/etf_eu_delivery_readiness_preflight_20260617_000001.json
```

WP12F validation proof:

```text
python tools/validate_etf_eu_delivery_readiness_preflight.py output/delivery/etf_eu_delivery_readiness_preflight_20260617_000001.json
ETF_EU_DELIVERY_READINESS_PREFLIGHT_OK

python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
15 passed

python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
22 passed

python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
30 passed

python -m pytest tests/test_etf_eu_delivery_receipt.py -q
22 passed

python -m pytest tests/test_etf_eu_email_dry_run.py -q
5 passed

python -m pytest tests/test_etf_eu_delivery_manifest.py -q
3 passed
```

WP12F current status:

```text
completed as readiness preflight refresh
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

## Current workflow posture

The main EU bootstrap workflow currently uses:

```text
pricing.build_ucits_valuation_prices_with_agreement
runtime.render_etf_eu_report_with_pricing_surface
runtime.etf_eu_fundability_surface
runtime.build_etf_eu_delivery_manifest
runtime.build_etf_eu_run_bundle
```

The workflow builds and validates report/pricing/fundability/delivery-manifest/run-bundle evidence only. WP12B, WP12C, WP12D, WP12E and WP12F are intentionally not workflow-integrated.

## Pending items

1. Consider WP13A explicit delivery-authority review decision, no send/no production delivery.
2. Recipient allowlist contract exists only as inactive/sample-only; no real recipients and no activation authority exist.
3. Mail setup policy exists only as sample-only/no-live-values; no mail-transport authority exists.
4. Receipt validator exists only as sample-only/not-delivery-proof; no real receipt authority exists.
5. WP13 real delivery enablement remains blocked until explicit delivery authority decision exists.
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
mail_setup_active=false
mail_transport_enabled=false
external_mail_api_enabled=false
ready_for_wp13_preflight_only=true
wp13_delivery_authority=false
```
