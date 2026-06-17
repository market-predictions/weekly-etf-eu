# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP13C related Codespace validation.

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
```

WP13C current status:

```text
implemented
selected_next_package=WP13D
selected_next_package_title=production recipient policy contract review, review-only
gap_domains_reviewed=recipient_policy, secure_transport_setup, receipt_proof_path
all_gap_statuses=gap_open
not workflow-integrated
related Codespace validation pending before full closeout
```

Next immediate action:

```text
python -m pytest tests/test_etf_eu_production_prerequisite_gap_review.py -q
python tools/validate_etf_eu_production_prerequisite_gap_review.py output/delivery/authority/etf_eu_production_prerequisite_gap_review_20260617_000000.json
python -m pytest tests/test_etf_eu_next_review_step_decision.py -q
python -m pytest tests/test_etf_eu_delivery_authority_review.py -q
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
python -m pytest tests/test_etf_eu_delivery_receipt.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
```

Only after these pass should WP13C be marked fully closed.

After WP13C closeout, next selected package:

```text
WP13D — production recipient policy contract review, review-only
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
