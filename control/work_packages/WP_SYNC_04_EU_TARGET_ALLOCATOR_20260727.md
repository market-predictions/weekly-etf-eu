# WP-SYNC-04 — EU Target Allocator and Controlled Transition Shadow

Date: 2026-07-27
Repository: `market-predictions/weekly-etf-eu`
Branch: `sync/donor-report-parity`
Status: in progress

## Objective

Translate the read-only donor exposure target into an investable EU/UCITS shadow target and compare three transition variants without mutating the official EU portfolio:

1. strict donor replication where an eligible implementation exists;
2. implementation-efficient maximum-eight-position target;
3. staged transition retaining temporary broad-core exposure while thematic sleeves are introduced.

## Inputs

- donor shared strategy state;
- donor shared exposure-level portfolio target;
- EU synchronization shadow;
- current EU portfolio state;
- merged shadow UCITS registry;
- fresh completed-close and liquidity evidence for mapped candidates.

## Required controls

- UCITS ETF, ISIN, KID and exact trading-line gates;
- completed-close price strictly before the allocator report date;
- non-authoritative connectivity prices cannot create funding authority;
- whole-share sizing;
- maximum eight funded positions;
- minimum residual cash reserve;
- explicit unresolved-exposure cash retention;
- concentration and broad-core overlap diagnostics;
- turnover and estimated cost reporting;
- no official portfolio, trade ledger, valuation history or delivery mutation.

## Shadow variants

### A. Strict mapped replication

Use donor target weights for every mapped and eligible exposure. Unresolved or blocked sleeves remain cash.

### B. Efficient eight-position implementation

Respect the eight-position limit. Prefer larger donor sleeves and combine or defer subscale sleeves only when the mapping contract explicitly permits it. No silent redistribution.

### C. Staged migration

Introduce eligible donor sleeves in controlled stages while temporarily retaining selected existing positions. Each stage must specify target cash, turnover, estimated cost, and unresolved exposure.

## Deliverables

- transition evidence basket and builder;
- evidence validator;
- EU target allocator;
- allocator validator;
- three variant JSON artifacts;
- comparison and preferred-variant artifact;
- sister-report allocation and transition surfaces;
- CI workflow with non-mutation and page-integrity gates;
- final handover with blockers and recommended activation boundary.

## Safety boundary

All outputs are shadow-only. No artifact in this work package has portfolio mutation, funding, execution, brokerage or production-delivery authority.
