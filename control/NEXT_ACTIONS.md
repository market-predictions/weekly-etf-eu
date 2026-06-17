# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP13B related Codespace validation.

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
```

WP13B current status:

```text
implemented
focused local validation passed
selected_next_package=WP13C
selected_next_package_title=production prerequisite gap review, review-only
not workflow-integrated
related Codespace validation pending before full closeout
```

WP13B focused validation:

```text
focused WP13B tests: 13 passed
next review step validator: OK
```

Next immediate action:

```text
python -m pytest tests/test_etf_eu_next_review_step_decision.py -q
python tools/validate_etf_eu_next_review_step_decision.py output/delivery/authority/etf_eu_next_review_step_decision_20260617_000000.json
python -m pytest tests/test_etf_eu_delivery_authority_review.py -q
python -m pytest tests/test_etf_eu_delivery_readiness_preflight.py -q
python -m pytest tests/test_etf_eu_recipient_allowlist.py -q
python -m pytest tests/test_etf_eu_smtp_secrets_policy.py -q
python -m pytest tests/test_etf_eu_delivery_receipt.py -q
python -m pytest tests/test_etf_eu_email_dry_run.py -q
python -m pytest tests/test_etf_eu_delivery_manifest.py -q
```

Only after these pass should WP13B be marked fully closed.

After WP13B closeout, next selected package:

```text
WP13C — production prerequisite gap review, review-only
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
