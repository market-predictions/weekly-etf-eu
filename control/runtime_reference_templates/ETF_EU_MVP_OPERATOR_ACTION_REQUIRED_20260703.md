# ETF EU MVP operator action required — 2026-07-03

## Required non-secret evidence values

```text
recipient_set_reference_id=<operator supplied non-secret reference>
recipient_set_hash=<operator supplied hash>
recipient_owner_approval_reference=<operator supplied non-secret reference>
recipient_rollback_reference=<operator supplied non-secret reference>
transport_reference_id=<operator supplied non-secret reference>
transport_presence_check_reference=<operator supplied non-secret reference>
transport_owner_approval_reference=<operator supplied non-secret reference>
transport_rollback_reference=<operator supplied non-secret reference>
explicit_mvp_preflight_authority_reference=<operator supplied non-secret reference>
```

## Do not commit

```text
plaintext recipient values
runtime-only private values
private access material
server access material
```

## Next human action

Replace placeholders in:

```text
control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md
```

Use non-secret references and hashes only.
