# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
REVIEW_WP_SYNC_00_08_DRAFT_PR_WITHOUT_ACTIVATION
```

PR #66 now contains a complete read-only synchronization architecture through cutover readiness. The next decision is whether to merge the shadow architecture into `main`. That decision must remain separate from portfolio activation and production-report replacement.

## Authoritative official baseline

```text
portfolio_position_count=3
cash_eur=60439.44
invested_market_value_eur=39317.32
nav_eur=99756.76
portfolio_mutation_performed=false
ledger_write_performed=false
```

| Ticker | Role | Shares | Value | Weight | Official action |
|---|---|---:|---:|---:|---|
| VWCE | Global core | 151 | €24,806.28 | 24.866766% | Hold |
| EUNA | Low-volatility carry diversifier | 1,526 | €7,465.04 | 7.483242% | Hold; no add or sale |
| SXR8 | U.S. equity overweight | 10 | €7,046.00 | 7.063180% | Hold; no second tranche |

No automatic add, reduction, exit, later tranche or satellite activation is authorized.

## Completed WP-SYNC-00/08 capability

The draft PR now delivers:

1. immutable donor shared strategy and portfolio-target contracts;
2. EU exposure-to-UCITS mapping with explicit evidence grades;
3. policy-driven Stage-1 shadow allocation;
4. incumbent overlap and EUNA risk-budget reviews;
5. non-optimizing composition replay;
6. explicit Stage-2 capacity and authority state machine;
7. donor-target versus donor-fresh-add distinction;
8. executive Dutch/English report parity;
9. Gmail-compatible multipart/related CID delivery;
10. Sent and Inbox receipt verification with privacy-minimal evidence;
11. a valid blocked activation package with state-oriented rollback.

Key evidence:

```text
donor_release=weekly_etf_shared_contract_v1_0_0
donor_commit=455201b4736dda41df07644d78b6797282a29fc7
validated_eu_design_commit=d33169fa513e22ac9197efe4fab9857ebaa6f85f
report_workflow_run=30410361517
replay_stage_2_workflow_run=30410361535
shadow_cid_delivery_run=30410951339
blocked_activation_package_run=30411531406
```

## Review-before-merge sequence

Before PR #66 leaves draft status:

1. Review the architecture as four separate layers:
   - decision framework;
   - input/state contract;
   - output contract;
   - operational runbook.
2. Confirm that the donor contract is consumed only through immutable release `v1.0.0`.
3. Confirm that the official portfolio and ledger hashes remain unchanged.
4. Review the Stage-1 policy limits and the two-sleeve allowlist.
5. Review the EUNA classification and Stage-2 source order.
6. Confirm that donor `hold_or_monitor` cannot become EU add authority.
7. Review the 11-page NL/EN report and CID email surface.
8. Review the 27 blockers in the activation package.
9. Prefer a squash merge because the PR contains a long development history.
10. Keep activation and production enablement out of the merge decision.

## After architecture merge: WP-SYNC-09

Only after the shadow architecture is accepted on `main`, create a separate work package:

```text
ETF-EU-WP-SYNC-09_FRESH_CUTOVER_EVIDENCE_AND_ACTIVATION_DECISION
```

Required evidence work:

1. Capture accepted current EUR Xetra-line valuation for VVSM and LOCK.
2. Capture timestamped Xetra bid, ask and quote size for both intended Stage-1 lines.
3. Capture and review the exact LOCK KID/PRIIPs artifact.
4. Refresh product evidence within the governed age limit.
5. Re-underwrite VVSM and LOCK using the latest donor strategy state.
6. Rebuild the allocator from fresh evidence rather than the dated connectivity cache.
7. Decide explicitly whether Stage 1 should be authorized.
8. If authorization is withheld, preserve the three-position portfolio and cash unchanged.
9. If authorization is granted later, create a new package with exact official-state mutation, ledger, rollback and receipt contracts.

## Stage-2 boundary

Stage 2 remains blocked even after Stage-1 evidence is complete unless:

- Stage 1 is separately authorized and applied;
- an official post-Stage-1 state and receipt exist;
- IXUA document, valuation and tradability grades pass;
- the donor emits a genuine fresh add direction, or a separate EU strategic-migration decision explicitly overrides the donor hold;
- a separate Stage-2 activation authorization exists.

Current Stage-2 capacity analysis is not an instruction:

```text
maximum_ixua_tranche_pct_nav=15.00
cash_source_pct_nav=10.569579
sxr8_source_pct_nav=4.430421
euna_source_pct_nav=0.00
executable_trade_intents=[]
```

## Delivery boundary

The CID transport path is technically validated in Gmail, but it remains shadow-only. A later production-delivery change must:

- reuse the validated multipart/related structure;
- retain four report attachments;
- preserve privacy-minimal receipt evidence;
- pass an independent production package and authorization gate;
- never treat SMTP success alone as an inbox receipt.

## Prohibited next actions

Do not:

- mutate `output/etf_eu_portfolio_state.json`;
- append to `output/etf_eu_trade_ledger.csv`;
- activate VVSM, LOCK or IXUA;
- replace the routine production report with the shadow report;
- send the shadow report again;
- infer authorization from PR merge, report text, historical replay or successful email delivery.
