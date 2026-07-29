# WP-SYNC-00/03 — EU Donor Strategy and Report Parity

Date: 2026-07-27
Status: claimed / implementation in progress
Branch: `sync/donor-report-parity`

## Purpose

Consume the Weekly ETF shared strategy decision state, map exposure-level conclusions to EU/UCITS products, compare them with the current EU model portfolio and generate a shadow sister report with the same executive structure and table contract as the donor.

## Authority boundaries

- Shadow output only.
- No model portfolio mutation.
- No trade intent activation.
- No email send.
- No production report replacement.
- No funding authority from the shared strategy state.
- ISIN, product type, KID status and exact trading-line verification remain authoritative for EU implementation.

## Inputs

- shared strategy state produced by `market-predictions/weekly-etf`;
- `output/etf_eu_portfolio_state.json`;
- `config/ucits_symbol_registry.yml`;
- `config/shared_exposure_ucits_map.yml`;
- current EU valuation history and pricing artifacts where available.

## Outputs

- normalized synchronization shadow state;
- machine-readable divergence rows with permitted reason codes;
- HTML/PDF sister-report preview following the donor's 16-section structure;
- standalone HTML with an embedded PNG portfolio curve;
- validation evidence for strategy parity, report structure and no-mutation boundaries.

## Required donor section parity

The shadow renderer must include equivalent sections and table shapes for:

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
9. Second-order effects
10. Current-position review
11. Best new opportunities / replacement analysis
12. Portfolio rotation plan
13. Final action table
14. Proposed position changes / rotation intents
15. Current positions and cash
16. Canonical next-run input

## Acceptance criteria

- every promoted donor exposure is represented in the EU shadow state;
- current EU positions are reconciled by ISIN/trading line, not report text;
- every strategic divergence has an allowed implementation reason code;
- mapped but unverified products remain blocked;
- no unresolved mapping is silently converted to cash or another exposure;
- HTML and PDF retain the same content hierarchy;
- the portfolio curve appears as a PNG/data asset in standalone HTML and PDF;
- production workflow and official portfolio files remain unchanged.
