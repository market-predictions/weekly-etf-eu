# Weekly ETF EU — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=CANONICAL_ACTIVE
project_repository=market-predictions/weekly-etf-eu
project_risk_class=financial_report_delivery_and_portfolio_state
adoption_status=enforced
enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md
workflow_authority_index=control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md
production_action=guarded_email_delivery
post_action_confirmation=independent_inbox_receipt_and_closeout_manifest
```

## User interface

The user provides one Weekly ETF EU instruction and receives one consolidated project status. The user does not separately direct the implementation and assurance roles.

## Local enforcement

- `/.github/workflows/run-weekly-etf-eu-routine.yml` is candidate-only and refuses `main`; it may build, machine-validate and persist generated candidate evidence only to the current candidate branch.
- `tools/build_etf_eu_release_assurance.py` retains a historical filename for compatibility but now produces only `etf_eu_release_evidence_preflight` machine evidence. It cannot issue an independent assurance verdict, merge authority or delivery authority.
- `tools/validate_etf_eu_release_assurance.py` rejects any machine-preflight record that claims independent assurance, merge authority or delivery authority.
- A separate `governance_release_assurance` reviewer must review one exact frozen candidate head and return `PASS | FAIL | INDETERMINATE`. Implementation may not self-certify.
- `/.github/workflows/send-weekly-etf-eu-controlled-transport.yml` is the sole active real delivery route. It is `main`-only and requires a committed guarded-delivery authority record that binds an independent PASS, an approved report commit and SHA-256 hashes for all six NL/EN client artifacts.
- The controlled transport sends the already-assured artifacts; it does not re-render them.
- Delivery is not confirmed until independent receipt and production closeout evidence exist.
- `tools/validate_etf_eu_workflow_authority.py` fail-closes historical workflow reactivation and parallel delivery paths.
- Issue #119 / PR #120 implementation ownership is reconciled in the machine-readable lifecycle record `control/ETF_EU_ARCHITECTURE_REV2_119_CLAIM.json`; it grants Worker-A implementation ownership only and does not grant assurance, integration, delivery, portfolio or broker authority.

## Authority separation

Machine evidence and independent assurance are distinct:

```text
machine evidence preflight
    -> supporting evidence only
    -> independent assurance still required
    -> no merge authority
    -> no delivery authority

independent governance_release_assurance PASS on exact frozen head
    -> merge may proceed if head is unchanged
    -> still no email authority

separately committed guarded-delivery authority
    -> exact approved artifacts may be transported
    -> no broker execution authority
```

## Cross-project authority

The shared standard and adoption registry are canonical in the private `market-predictions/control-plane` repository. The cross-project files retained in this repository are migration provenance and compatibility history, not current shared authority.

ETF EU project-specific instrument, state, portfolio, report, recipient, delivery, workflow, and closeout authority remains local to this repository.
