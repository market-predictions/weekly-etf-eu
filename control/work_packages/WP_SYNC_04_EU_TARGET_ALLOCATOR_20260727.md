# WP-SYNC-04 — EU Target Allocator and Controlled Transition Design

Date: 2026-07-27
Repository: `market-predictions/weekly-etf-eu`
Branch: `sync/eu-target-allocator`
Status: in progress, shadow only

## Objective

Transform the validated Weekly ETF donor exposure target into comparable EU/UCITS portfolio variants without mutating the official EU portfolio or authorizing funding, trading, delivery or model execution.

## Required variants

1. **Strict donor replication**
   - preserve all donor exposure weights;
   - map every exposure to a verified EU/UCITS trading line;
   - retain the donor cash target;
   - report, but do not conceal, the nine-position breach against the eight-position policy.

2. **Efficient eight-position implementation**
   - preserve donor weights wherever possible;
   - combine the 0.53% utilities sleeve with grid/infrastructure only when the selected implementation has material utility/infrastructure exposure;
   - retain the donor cash target;
   - do not create a sub-1% standalone position merely to copy a ticker count.

3. **Staged transition**
   - Stage A is cash-led and adds the five largest mapped donor exposures at partial size while retaining VWCE, EUNA and SXR8;
   - Stage A must remain at or below eight positions and maintain at least 10% cash;
   - Stage B may remove incumbents and complete the efficient eight-position target only after fresh evidence and a separate transition review;
   - no stage is an execution instruction.

## Allocator inputs

- donor shared strategy state;
- donor exposure-level portfolio target;
- current official EU portfolio state;
- merged production plus supplemental shadow UCITS registry;
- completed-close pricing and liquidity evidence;
- explicit policy and cost assumptions.

## Evidence policy

Funding eligibility in the shadow model requires:

- confirmed UCITS ETF identity;
- exact ISIN;
- verified EUR trading line;
- issuer KID/PRIIPs document availability;
- completed close strictly before the allocator report date;
- usable whole-share price;
- preliminary liquidity evidence;
- no unresolved product-policy blocker.

Yahoo/yfinance evidence is connectivity and market-observation evidence only. It is not authoritative valuation or execution evidence.

## Portfolio policy

- base currency: EUR;
- maximum final positions: 8;
- minimum efficient standalone target: 1.0% of NAV;
- final cash target: donor cash target;
- Stage A minimum cash: 10.0% of NAV;
- no single exposure above 30.0%;
- whole shares only;
- unresolved or rounded capacity remains cash;
- broad incumbent funds are not counted as exact substitutes for dedicated donor exposures;
- product mappings do not authorize allocations.

## Cost policy

Report a cost envelope rather than broker-specific precision:

- observed quote spread when available;
- 5 bps low commission/slippage scenario;
- 10 bps base scenario;
- 20 bps stress scenario;
- gross traded notional and one-way turnover reported separately.

## Liquidity policy

Preliminary minimum median 20-session EUR traded value:

- target weight above 10%: EUR 250,000/day;
- target weight from 3% through 10%: EUR 100,000/day;
- target weight below 3%: EUR 50,000/day.

Quote-spread warning threshold: 60 bps. Missing quote-spread evidence remains a review blocker but does not invalidate completed-close observation.

## Safety boundary

This work package must not:

- change `output/etf_eu_portfolio_state.json`;
- write an official trade intent;
- alter valuation history;
- generate a guarded-send request;
- send an email;
- merge either synchronization PR;
- claim broker-specific executability.

## Acceptance gates

- all three variants reconcile to 100% including cash;
- strict variant reports its position-limit failure;
- efficient variant has no more than eight positions;
- Stage A has no more than eight positions and at least 10% cash;
- every security has identity, price, liquidity and blocker lineage;
- whole-share units and residual cash reconcile;
- turnover and cost scenarios reconcile;
- official portfolio mutation remains false;
- results are deterministic apart from generation timestamps.
