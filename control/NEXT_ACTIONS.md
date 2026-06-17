# Weekly ETF EU Review OS — Next Actions

Current priority: finish WP13I related Codespace validation.

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
WP13E
WP13F
WP13G
WP13H
```

WP13I current status:

```text
implemented
selected_next_package=WP14A
selected_next_package_title=post-WP13 roadmap lane selection, review-only
decision=blocked_state_closed
wp13_review_chain_complete=true
delivery_authority_not_granted=true
operational_prerequisites_complete=false
production_delivery=false
wp13_authority=false
roadmap_loop_closed=true
not workflow-integrated
related Codespace validation pending before full closeout
```

Next immediate action:

```text
python -m pytest tests/test_etf_eu_wp13i_blocked_state_closeout.py -q
python tools/validate_etf_eu_wp13i_blocked_state_closeout.py output/delivery/authority/etf_eu_wp13i_blocked_state_closeout_20260617_000000.json
python -m pytest tests/test_etf_eu_wp13h_explicit_authority_review.py -q
python -m pytest tests/test_etf_eu_delivery_authority_prerequisite_reconciliation.py -q
python -m pytest tests/test_etf_eu_receipt_proof_contract_review.py -q
python -m pytest tests/test_etf_eu_secure_transport_setup_contract_review.py -q
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

Only after these pass should WP13I be marked fully closed.

After WP13I closeout, next selected package:

```text
WP14A — post-WP13 roadmap lane selection, review-only
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
