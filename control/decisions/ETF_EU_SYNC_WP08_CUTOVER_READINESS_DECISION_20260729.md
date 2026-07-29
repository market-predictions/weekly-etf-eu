# ETF EU WP-SYNC-08 Cutover Readiness Decision — 2026-07-29

## Decision status

```text
architecture_validated=true
shadow_delivery_validated=true
activation_package_validated=true
activation_ready=false
portfolio_mutation=false
ledger_write=false
```

## Stable decisions

### 1. Donor target and donor action are separate authorities

A non-zero donor target weight may describe an existing donor holding. It does not automatically mean the EU portfolio should establish the corresponding exposure.

The shared state must expose and consumers must distinguish:

```text
donor_target_present
donor_fresh_add_direction
```

A donor `hold` or `hold_or_monitor` state does not authorize an EU add. IXUA Stage-2 readiness therefore requires either:

- a genuine donor `add_candidate` direction; or
- a separate EU strategic-migration decision.

No such migration override currently exists.

### 2. Registry expansion cannot reopen Stage 1

Stage-1 selection is policy-governed, not registry-driven.

The accepted Stage-1 candidate set is:

```text
ai_compute_infrastructure
cyber_security
```

New UCITS mappings may improve research coverage and later-stage readiness, but they cannot silently enter Stage 1 or rewrite the strict/fixed-50 comparison variants.

### 3. EUNA is a carry diversifier, not a crisis hedge

EUNA is retained at its existing capped weight for Stage 1 because it reduces risk relative to pro-rata risky-asset reallocation. It is not described as a reliable short-horizon equity hedge.

```text
stage_1=hold_current_position_no_add_no_sale
stage_2_funding_priority=third
automatic_sale=false
```

### 4. Stage 2 is a readiness state machine

Stage 2 does not contain hard-coded executable orders. It evaluates:

- official Stage-1 state and receipt;
- product evidence grades;
- donor direction;
- EUNA risk budget;
- funding-source capacity;
- separate authorization.

A blocked artifact with complete blocker disclosure and no executable intents is a successful control result.

### 5. Rollback is state-oriented

Rollback preserves accepted official state hashes and requires a separate package and authorization. The system must not:

- infer reverse orders from report text;
- automatically rewrite the ledger;
- automatically create reverse transactions.

### 6. Email chart delivery uses multipart/related CID

The Gmail-compatible delivery structure is:

```text
multipart/mixed
└── multipart/related
    ├── multipart/alternative
    │   ├── text/plain
    │   └── text/html with cid reference
    └── image/png with matching Content-ID
└── four report attachments
```

SMTP success and inbox receipt are separate facts. Production delivery may be claimed only after both transport evidence and mailbox receipt evidence exist.

### 7. Privacy-minimal mailbox evidence is sufficient

Receipt evidence may store:

- hashed message identifiers;
- non-sensitive subject and run lineage;
- attachment names, sizes and digests;
- inline-image name, size, digest and Content-ID;
- Sent/Inbox match booleans.

It must not store recipient plaintext or raw MIME.

### 8. Architecture merge is not activation

These remain separate decisions:

1. merge the synchronization architecture;
2. promote the sister report into production;
3. authorize Stage 1;
4. authorize Stage 2;
5. mutate official state and ledger.

PR #66 may be reviewed as shadow architecture while every portfolio and activation authority remains false.

## Validated evidence

```text
donor_contract_commit=455201b4736dda41df07644d78b6797282a29fc7
validated_eu_design_commit=d33169fa513e22ac9197efe4fab9857ebaa6f85f
report_workflow_run=30410361517
replay_stage_2_workflow_run=30410361535
shadow_cid_delivery_run=30410951339
blocked_activation_package_run=30411531406
blocked_activation_package_artifact=8708563958
blocked_activation_package_digest=sha256:cb3880c366a18b066ca8895dbd5da9c213ca580da2121376f59f556b0a4b0ed4
```

## Consequence

WP-SYNC-08 is complete at the cutover-readiness boundary. The next work package is fresh cutover evidence and a separate activation decision, only after the shadow architecture is reviewed and accepted.
