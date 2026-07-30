# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
PRESERVE_OFFICIAL_PORTFOLIO_UNTIL_ACCEPTED_XETRA_MARKET_EVIDENCE_AND_DONOR_FRESH_ADD_EXIST
```

The synchronization architecture is merged and WP-SYNC-09 is complete. Stage 1 is explicitly blocked, not pending an implementation fix. The official portfolio must remain unchanged until both activation-grade market evidence and current donor fresh-add authority exist.

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

## Completed architecture and WP-SYNC-09 capability

The repository now contains:

1. immutable donor strategy and portfolio-target consumption;
2. ISIN-first EU exposure mapping;
3. policy-constrained Stage-1 and Stage-2 shadow allocation;
4. incumbent overlap and EUNA risk-budget review;
5. validated bilingual sister-report output contract;
6. Gmail-compatible shadow CID delivery and receipt evidence;
7. blocked cutover packaging;
8. fresh exact identity and KID capture for VVSM and LOCK/L0CK;
9. exact Deutsche Börse line validation by ISIN, WKN, symbol, Xetra and EUR;
10. current donor re-underwriting;
11. fail-closed market-evidence and activation-decision machinery;
12. before/after official-state hash protection.

WP-SYNC-09 evidence:

```text
workflow_run=30501245612
artifact_id=8743584959
artifact_digest=sha256:48ec8c7fcdddcf016378ba19dc0398dadd4432404ea240618d054117fa09e2fc
identity_pass_count=2
kid_pass_count=2
accepted_close_pass_count=0
timestamped_quote_pass_count=0
liquidity_pass_count=0
decision=blocked
decision_blocker_count=7
```

## Conditions required before reopening Stage 1

Do not reopen activation work unless both categories below have materially changed.

### A. Accepted exact Xetra market evidence

For both VVSM and L0CK:

- accepted current completed Xetra EUR close;
- timestamped Xetra bid and ask;
- timestamped quote size;
- accepted 20-session liquidity measurement;
- source lineage and evidence age within policy limits.

A different-currency issuer NAV, daily OHLCV, a search snippet or the 2026-07-24 cache does not satisfy this category.

### B. Current donor fresh-add authority

The current donor scorecard must emit a genuine fresh-add direction for the relevant exposure. Target presence, current ownership, `hold`, `hold_with_override`, or `hold_or_monitor` are not add authority.

Current donor evidence remains:

```text
SMH=hold_with_override; smaller / under review
CIBR=hold; hold / monitor
fresh_add_direction_present=false
```

## When a dependency changes

Create a new dated evidence run rather than reusing WP-SYNC-09 artifacts. The new package must:

1. pin the current donor evidence commit;
2. capture exact current product and market evidence;
3. compare official portfolio and ledger hashes before and after;
4. rebuild the allocator only from accepted evidence;
5. create a new explicit activation decision;
6. preserve `executable_trade_intents=[]` until a separate authorization package is approved;
7. keep any official state mutation, ledger write, rollback and execution receipt in a later separately authorized package.

## Stage-2 boundary

Stage 2 remains blocked unless:

- Stage 1 is separately authorized and applied;
- an official post-Stage-1 state and receipt exist;
- IXUA document, valuation and tradability grades pass;
- the donor emits a genuine fresh add direction, or a separate EU strategic-migration decision explicitly overrides the donor hold;
- a separate Stage-2 activation authorization exists.

Current Stage-2 capacity analysis remains non-executable:

```text
maximum_ixua_tranche_pct_nav=15.00
cash_source_pct_nav=10.569579
sxr8_source_pct_nav=4.430421
euna_source_pct_nav=0.00
executable_trade_intents=[]
```

## Operational discipline

Do not schedule repeated blind high-frequency probes against the same official endpoints. The latest fresh run established stable external behavior:

```text
completed_close_endpoint=HTTP_200_EMPTY_JSON_OBJECT
history_crosscheck=HTTP_200_EMPTY_JSON_OBJECT
timestamped_quote_endpoint=TIMEOUT
```

A new run is warranted only after a source, endpoint, entitlement, donor action or policy authority changes.

## Prohibited next actions

Do not:

- mutate `output/etf_eu_portfolio_state.json`;
- append to `output/etf_eu_trade_ledger.csv`;
- activate VVSM, LOCK/L0CK or IXUA;
- create executable trade intents;
- replace the routine production report with a shadow report;
- send a new shadow report;
- infer authorization from a merged capability, green CI, exact KID, report text, historical target weight or successful email delivery.
