# Weekly ETF US–EU Synchronization Roadmap

Date: 2026-07-27
Status: implementation in progress on isolated shadow branch
Repositories:
- donor and strategy authority: `market-predictions/weekly-etf`
- EU/UCITS implementation and sister report: `market-predictions/weekly-etf-eu`

## Objective

Bring Weekly ETF EU into strategic, structural and visual alignment with Weekly ETF without copying US tickers blindly and without weakening EU/UCITS product controls.

Synchronization means:

1. both reports consume the same market/regime and lane-ranking decision state;
2. both reports reach the same exposure-level conclusions;
3. the US and EU portfolios may differ only for explicit implementation, product, currency, liquidity, concentration, turnover or execution reasons;
4. every material divergence is machine-readable and client-visible;
5. Weekly ETF EU uses the same executive-level section and table contract as Weekly ETF;
6. production portfolio state, trade ledgers and delivery remain separately controlled.

## Architectural decision

Use one donor strategy decision state with two implementation adapters.

```text
Weekly ETF market, regime, discovery and re-underwriting engine
                         |
             shared strategy decision state
                  /                    \
        US implementation          EU/UCITS adapter
        and portfolio state        and portfolio state
                  \                    /
             sister report surfaces
```

The shared state is exposure-first. It identifies themes and portfolio roles such as semiconductor compute, cybersecurity resilience, grid electrification, developed ex-US equity or aggregate bonds. It does not require the US and EU reports to hold the same ticker.

## Non-negotiable boundaries

- No official US or EU portfolio mutation during WP-SYNC-00 through WP-SYNC-03.
- No report send from the synchronization branch.
- No EU allocation authority from a US-listed ETF ticker.
- ISIN and verified trading line remain authoritative for EU products.
- The existing EU strategic allocation remains a legacy comparison baseline, not future strategy authority.
- English and Dutch EU reports must derive from one normalized state and may not run separate research.
- The donor production report must remain materially unchanged while the shared contract is extracted.

## Donor report section contract

The synchronized EU sister report must implement the same numbered content sequence and equivalent tables:

1. Executive summary
2. Portfolio actions
2A. Decision cockpit
3. Regime dashboard
4. Structural opportunity radar
4A. Short / avoidance radar
5. Key risks and invalidations
6. Bottom line
7. Portfolio curve and development
7A. Current-position performance
8. Allocation map
9. Second-order effects map
10. Current-position review
11. Best new opportunities and replacement analysis
12. Portfolio rotation plan
13. Final action table
14. Proposed position changes / rotation intents
15. Current positions and cash
16. Canonical next-run input

EU-specific implementation evidence is added inside these sections and as a compact divergence table, rather than replacing donor sections.

## Work packages

### WP-SYNC-00 — architecture and baseline

Deliverables:
- source-of-truth comparison;
- donor component inventory;
- report section/table contract;
- state and delivery boundaries;
- baseline portfolio exposure comparison;
- rollback rules.

### WP-SYNC-01 — shared strategy decision state

Weekly ETF exports a versioned JSON artifact containing:
- run and pricing lineage;
- regime and confidence;
- complete assessed lane set;
- promoted opportunity ranking;
- neutral market score separated from portfolio-context adjustments;
- exposure-level desired action and target range;
- evidence, invalidation and concentration constraints;
- no execution or funding authority.

### WP-SYNC-02 — UCITS mapping and implementation scoring

Weekly ETF EU maps each shared exposure to zero or more UCITS candidates with:
- ISIN, fund, exchange, trading line and currency;
- KID/PRIIPs and UCITS status;
- TER, liquidity, spread and structure where available;
- exposure-purity and overlap notes;
- verification and pricing status;
- implementation blocker reason codes.

### WP-SYNC-03 — EU synchronization shadow state

Produce a read-only comparison of:
- shared target exposure;
- current EU exposure;
- preferred UCITS implementation;
- desired versus actual weight;
- action candidate;
- blocker or divergence reason.

### WP-SYNC-04 — sister-report renderer

Build a shadow HTML/PDF renderer that mirrors the donor:
- executive cockpit and hierarchy;
- section order and tables;
- typography, spacing, cards, borders and functional status colors;
- portfolio curve as a mail-safe PNG/CID asset;
- equivalent print and receiving-mail-client behavior.

### WP-SYNC-05 — parity and visual gates

Hard checks:
- same shared-state identifier and report date;
- same regime and promoted exposure ranking;
- same exposure direction and evidence;
- no unexplained strategic divergence;
- every EU deviation has a permitted reason code;
- all donor sections and required table columns present;
- chart visible in PDF, attached HTML and receiving email;
- no stale holdings or unsupported product claims.

### WP-SYNC-06 — shadow runs and transition proposal

Run historical and current side-by-side comparisons. Produce a staged EU transition proposal but do not change the official model portfolio without separate authorization.

### WP-SYNC-07 — controlled cutover

Only after review:
- promote shared strategy state to production input;
- promote EU sister-report renderer;
- separately authorize any portfolio transition;
- preserve rollback to the last validated EU production package.

## Permitted divergence reason codes

- `no_ucits_equivalent`
- `ucits_identity_unverified`
- `kid_missing`
- `trading_line_unverified`
- `pricing_missing_or_stale`
- `liquidity_below_threshold`
- `currency_policy_blocked`
- `product_type_blocked`
- `whole_share_rounding`
- `position_limit`
- `factor_overlap_limit`
- `turnover_guard`
- `cash_reserve`
- `existing_position_transition`

## Definition of done

The systems are synchronized when they agree on market regime, ranked opportunities, desired exposure direction and risk constraints, while any difference in instrument or weight is explicitly attributable to EU implementation constraints. Identical ticker sets are not required; unexplained strategic divergence is not allowed.
