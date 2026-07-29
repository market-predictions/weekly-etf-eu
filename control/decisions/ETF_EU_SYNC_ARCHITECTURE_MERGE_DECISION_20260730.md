# ETF EU synchronization architecture merge decision

**Date:** 2026-07-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Pull request:** #66  
**Decision scope:** shadow architecture merge only

## Decision

The WP-SYNC-00/08 synchronization architecture is accepted for squash merge into `main`.

This decision accepts the architecture as reusable repository capability. It does not accept or authorize Stage 1, Stage 2, official portfolio mutation, ledger mutation, trade execution, production-report replacement or production delivery.

## Four-layer review

### 1. Decision framework

Accepted because:

- Stage-1 exposure selection is explicitly frozen to AI compute/semiconductors and cybersecurity;
- incumbents are retained and incumbent sales are prohibited in Stage 1;
- turnover, cash, position-count, concentration, price-age and liquidity controls are explicit;
- donor target presence and donor fresh-add direction remain separate authorities;
- Stage 2 remains blocked and has no executable trade intents.

### 2. Input/state contract

Accepted because:

- donor consumption is pinned to immutable release `weekly_etf_shared_contract_v1_0_0`;
- donor commit is fixed at `455201b4736dda41df07644d78b6797282a29fc7`;
- mutable donor branches are prohibited;
- official portfolio and trade-ledger files are not modified by PR #66;
- UCITS identity, document, valuation and tradability evidence grades remain separate;
- cached connectivity evidence remains non-authoritative.

### 3. Output contract

Accepted because:

- donor section and table-header parity is restored after all late overlays;
- Dutch and English reports both contain 19 required sections and 11 physical pages;
- all machine validators pass;
- visual review found no blank pages, clipping, overlap or orphaned rows;
- internal machine identifiers are excluded from visible client text while metadata lineage remains available;
- output rendering cannot create allocation or authority.

Validated report evidence:

```text
validated_code_head=034b5f93056d36dfc7a6048b43b650ff434c0516
workflow_run_id=30499071087
artifact_id=8742768136
artifact_digest=sha256:f6cad390bc41502f40b7d38cd14f83f34734c63f3e65cb15093ef3474a3f16d2
```

### 4. Operational runbook

Accepted because:

- current PR workflows are green;
- production state and production delivery workflows are not replaced;
- shadow CID delivery is restricted to exactly one self-recipient;
- delivery requires explicit confirmation, a successful source workflow, exact source SHA and exact shadow branch;
- mailbox evidence stores hashes and counts, not recipient plaintext or raw MIME;
- the activation package is deliberately blocked and rejects any authority escalation.

Current green workflow matrix:

```text
30499071074 strategy synchronization
30499071060 cutover product evidence
30499071076 target allocator
30499071107 transition composition replay
30499071087 allocator report
30499071090 shadow CID transport
30499071109 shadow CID live-delivery validation
30499071071 blocked activation package
```

## Merge method

Use a squash merge because PR #66 contains a long iterative branch history. The squash commit must describe the merge as shadow architecture only.

## Post-merge state

After merge:

```text
architecture_available_on_main=true
stage_1_activation_authorized=false
stage_2_activation_authorized=false
portfolio_mutation=false
ledger_write=false
execution_authority=false
production_report_replacement=false
production_delivery_authority=false
```

## Next work package

The next development package is:

```text
ETF-EU-WP-SYNC-09_FRESH_CUTOVER_EVIDENCE_AND_ACTIVATION_DECISION
```

WP-SYNC-09 must begin with fresh accepted Xetra valuation/spread evidence for VVSM and LOCK, exact LOCK KID capture and current donor re-underwriting. Activation requires a separate explicit decision and must fail closed if evidence remains incomplete.
