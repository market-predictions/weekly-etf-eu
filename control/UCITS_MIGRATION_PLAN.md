# UCITS Migration Plan

## Phase 0 — repo clone

Status: done.

`market-predictions/weekly-etf-eu` was cloned from `market-predictions/weekly-etf`.

## Phase 1 — authority separation

Status: in progress.

Tasks:

- rewrite control layer for EU/UCITS authority;
- add UCITS review contract;
- add investability rules;
- add symbol registry contract;
- add EU config stubs;
- add EU cash-only state;
- add no-U.S.-ETF-as-holding validator.

## Phase 2 — workflow isolation

Status: planned.

Tasks:

- disable inherited production send workflow;
- introduce `send-weekly-etf-eu-report.yml`;
- introduce `weekly_etf_eu_report_request_*` run queue;
- rename output files to `weekly_etf_eu_review_*`.

## Phase 3 — UCITS instrument registry

Status: planned.

Tasks:

- verify candidate UCITS ETFs by ISIN;
- map U.S. proxies to UCITS candidates;
- validate KID / PRIIPs availability;
- validate exchange lines and trading currencies;
- add liquidity and TER fields where available.

## Phase 4 — pricing migration

Status: planned.

Tasks:

- price UCITS exchange lines;
- preserve U.S. proxy pricing only as benchmark/reference data;
- add provider symbol and exchange lineage;
- ensure price rows disclose trading currency and exchange.

## Phase 5 — Dutch-first report

Status: planned.

Tasks:

- render Dutch report as primary EU client output;
- disclose UCITS, ISIN, KID, trading line and currency;
- label U.S. proxies as research-only;
- block U.S. tickers from portfolio holdings tables.

## Phase 6 — delivery enablement

Status: blocked.

Delivery can be enabled only after EU validators pass and the report is no longer using cloned U.S. state as EU current truth.
