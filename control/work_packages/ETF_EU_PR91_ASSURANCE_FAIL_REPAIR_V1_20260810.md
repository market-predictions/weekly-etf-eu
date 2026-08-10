# ETF EU PR91 Assurance-Fail Repair V1

Date: 2026-08-10
Parent work package: `ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1`
Parent issue: #90
Failed assurance issue: #92
Pull request: #91
Owner role: `implementation_operations`
Status: `ACTIVE`

## Trigger
Independent role-B assurance returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

on frozen head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

The failed head remains historical assurance evidence. It is not merge-authorized and not delivery-authorized.

## Accepted blockers

### P0-A — Canonical pricing v2 contract
Repair one coherent executable contract across:

`provider qualification → v2 pricing artifact → v2 validator → normalized report state → candidate package`

Acceptance criteria:
- canonical schema is `ucits_close_price_validation_basket_results_v2`;
- candidate request report date is passed explicitly to pricing generation;
- funded two-provider same-date consensus is mandatory and fail-closed;
- exact funded lines in protected state must all have qualifying pricing evidence;
- validator and normalized-state builder consume the same v2 contract;
- report-date drift, v1 schema and one-provider funded evidence fail;
- no pricing compatibility field becomes current authority.

### P0-B — State-derived Markdown delivery artifacts
Repair NL/EN Markdown so they are derived from protected/current normalized state rather than hard-coded three-position copy.

Acceptance criteria:
- funded count is dynamic;
- every funded ticker, including L0CK, is present;
- no hard-coded VWCE/EUNA/SXR8-only current-position copy;
- three-position wording fails closed;
- retired strategic/phase targets and fixed 7.50% reserve wording fail closed;
- both Markdown artifacts are validated as delivery artifacts alongside HTML/PDF.

### P0-C — End-to-end candidate regression
Produce executable evidence on the repaired semantic head that traverses the candidate pricing/normalized-state/Markdown contract end to end and proves the two failed defect classes are covered.

The final frozen repair head must also pass the normal PR gates. Any subsequent semantic change requires a new validation cycle.

## Protected boundaries
Throughout this repair:
- portfolio mutation = false;
- trade-ledger write = false;
- real broker execution = false;
- report delivery = false;
- SMTP send = false;
- existing allocation-authority decisions remain unchanged.

## Handover and assurance
When all acceptance criteria pass:
1. write a new repair implementation handover as the final candidate mutation;
2. freeze the resulting exact PR #91 head;
3. open a fresh independent assurance issue distinct from #92;
4. require `PASS | FAIL | INDETERMINATE` on that exact new SHA;
5. merge only after PASS and unchanged head.

Issue #92 remains the assurance record for the failed historical head.
