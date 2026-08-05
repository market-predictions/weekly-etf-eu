# Weekly ETF EU — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
project_repository=market-predictions/weekly-etf-eu
project_risk_class=financial_report_delivery_and_portfolio_state
adoption_status=enforced
enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md
production_action=guarded_email_delivery
post_action_confirmation=independent_inbox_receipt_and_closeout_manifest
```

## User interface

The user provides one Weekly ETF EU instruction and receives one consolidated project status. The user does not separately direct the implementation and assurance roles.

## Local enforcement

- `tools/build_etf_eu_release_assurance.py` reconstructs the candidate from run identity, manifests, visual review, delivery queue, and exact artifact hashes.
- `tools/validate_etf_eu_release_assurance.py` rejects incomplete, failed, contradictory, or self-certified evidence.
- `.github/workflows/run-weekly-etf-eu-routine.yml` requires assurance `PASS` before guarded transport.
- Delivery is not confirmed until independent receipt and production closeout evidence exist.

## Interim canonical-host duty

Until `market-predictions/control-plane` is created, this repository temporarily hosts the cross-project standard and adoption register. ETF EU project-specific authority remains separate from the generic standard.
