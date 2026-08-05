# Project Governance Bootstrap Template

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=<canonical GitHub path>
project_repository=<owner/repository>
project_risk_class=<risk classification>
adoption_status=<planned|documented|partially_enforced|enforced>
enforcement_maturity=<LEVEL_0...LEVEL_4>
implementation_role=implementation_operations
assurance_role=governance_release_assurance
```

## User interface

The user gives one project instruction and receives one consolidated status. The user does not separately coordinate the two roles.

## Local assurance extension

```text
project_specific_assurance_contract=<path>
production_action=<send|deploy|publish|migrate|delete|mutate|none>
post_action_confirmation=<receipt|target_state_check|deployment_health|inbox_confirmation|none>
```

## Required local behavior

- Implementation produces an identifiable release candidate.
- Governance reconstructs it from authoritative evidence.
- Implementation cannot issue governance `PASS`.
- Governance cannot silently modify the candidate under review.
- A repaired candidate receives a new assurance pass.
- Completion is not claimed before the required post-action confirmation exists.

## Session read rule

After `SYSTEM_INDEX`, `CURRENT_STATE`, and `NEXT_ACTIONS`, read this bootstrap before production, release, delivery, deployment, migration, deletion, or consequential state mutation work.
