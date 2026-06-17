# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP13E related Codespace validation.

Completed:

```text
WP9
WP10
WP10B
WP11
WP12
WP12B
WP12C
WP12D
WP12E
WP12F
WP13A
WP13B
WP13C
WP13D
```

WP13E current status:

```text
implemented
selected_next_package=WP13F
selected_next_package_title=receipt proof contract review, review-only
transport_state=sample_only_no_secrets
future_transport_controls_defined=true
smtp_configured=false
secrets_present=false
mail_transport_enabled=false
external_mail_api_enabled=false
wp13_authority=false
production_delivery=false
not workflow-integrated
related Codespace validation pending before full closeout
```

Next immediate action:

```text
python -m pytest tests/test_etf_eu_secure_transport_setup_contract_review.py -q
python tools/validate_etf_eu_secure_transport_setup_contract_review.py output/delivery/authority/etf_eu_secure_transport_setup_contract_review_20260617_000000.json
python -m pytest tests/test_etf_eu_recipient_policy_contract_review.py -q
python -m pytest tests/test_etf_eu_production_prerequisite_gap_review.py -q
python -m pytest tests/test_etf_eu_next_review_step_decision.py -q
python -m pytest tests/test_etf_eu_delivery_authority_review.py -q
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
python -m pytest tests/test_etf_eu_delivery_receipt.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
```

Only after these pass should WP13E be marked fully closed.

After WP13E closeout, next selected package:

```text
WP13F — receipt proof contract review, review-only
```

Boundary rule:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
ready_for_wp13_preflight_only=true
wp13_authority=false
```
