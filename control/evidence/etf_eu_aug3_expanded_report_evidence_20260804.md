# Weekly ETF EU — 2026-08-03 expanded report evidence

## Final validated runtime

```text
repository=market-predictions/weekly-etf-eu
pull_request=71
branch=routine/20260803-expanded-funded-report
validated_runtime_sha=d9f49c6f729cb632e77f8b21f9558eeefc5f6b1c
report_date=2026-08-03
report_suffix=260803_05
run_id=20260803_30860298693_1
workflow_run=30860298693
workflow_job=91840542978
workflow_conclusion=success
artifact_id=8874130446
artifact_sha256=f451dc03ae726bcab519be21a566b72369c51f8396bb6e572624b16a3525fa57
artifact_size_bytes=5308760
```

The exact runtime passed current macro-context construction, two-provider funded pricing, controlled-universe pricing, valuation reconciliation, allocator validation, state validation, Dutch and English report validation, exact four-file package validation, complete PDF rendering and protected-state proof.

## Decision framework

The report distinguishes three different outcomes:

1. **official funded portfolio** — the protected positions and cash actually stored in the model state;
2. **current monitored opportunity universe** — mapped UCITS lines with current completed-close evidence;
3. **model expansion proposal** — analytical quantities that remain unexecuted until all activation gates pass.

A larger ticker set or a calculated order is not automatically a funded position. Portfolio mutation requires current price and identity evidence, accepted liquidity, timestamped bid/ask/quote-size evidence, donor direction where required, and explicit model-capital activation authority.

## Current pricing contract

Fresh report-date pricing uses:

```text
Deutsche Börse/Xetra exact ISIN+MIC session close
+
Yahoo Chart exact symbol/venue/currency agreement
```

The Yahoo adapter includes a rollover-safe fallback for German daily bars: `regularMarketPrice` is accepted only when `regularMarketTime` resolves to the requested report date in Europe/Berlin and the observation is demonstrably after that session. The result still requires independent Deutsche Börse agreement.

```text
controlled_line_count=13
priced_line_count=13
funded_consensus_count=3/3
funded_identity_anchor_count=3/3
report_pricing_gate_passed=true
```

| Ticker | Close | Date | Evidence status |
|---|---:|---|---|
| VWCE | €165.10 | 2026-08-03 | two-provider consensus |
| EUNA | €4.8969 | 2026-08-03 | two-provider consensus |
| SXR8 | €709.52 | 2026-08-03 | two-provider consensus |
| L0CK | €10.5940 | 2026-08-03 | two-provider consensus |
| VVSM | €88.15 | 2026-08-03 | two-provider consensus |

All thirteen controlled lines received a positive current close. Some non-funded research lines remain single-source evidence and therefore do not receive funded-consensus authority.

## Official run-scoped valuation

The official portfolio remains three positions:

| Position | Shares | Current close | Market value |
|---|---:|---:|---:|
| VWCE | 151 | €165.10 | €24,930.10 |
| EUNA | 1,526 | €4.8969 | €7,472.67 |
| SXR8 | 10 | €709.52 | €7,095.20 |

```text
cash_eur=60439.44
invested_market_value_eur=39497.97
nav_eur=99937.41
official_position_count=3
portfolio_mutation=false
ledger_write=false
real_broker_execution=false
```

## Evidence-qualified model expansion proposal

The staged allocator selected two additional analytical positions:

| Ticker | Proposed shares | Close | Target weight | Gross value |
|---|---:|---:|---:|---:|
| VVSM | 168 | €88.15 | 14.845310% | €14,809.20 |
| L0CK | 956 | €10.5940 | 10.152559% | €10,127.86 |

```text
proposed_position_count=5
projected_cash_eur=35477.44
projected_cash_weight_pct=35.563945
gross_buy_value_eur=24937.06
gross_turnover_pct_nav=24.997869
estimated_transaction_cost_eur=24.94
```

This is a model proposal only. It was not applied to official state.

Remaining blockers:

```text
VVSM:timestamped_bid_ask_quote_size
L0CK:timestamped_bid_ask_quote_size
donor_fresh_add_direction_absent
explicit_model_capital_activation_confirmation_absent
```

## Client package

```text
nl_html=output/fresh_generation/weekly_etf_eu_review_nl_260803_05.html
nl_pdf=output/fresh_generation/weekly_etf_eu_review_nl_260803_05.pdf
en_html=output/fresh_generation/weekly_etf_eu_review_260803_05.html
en_pdf=output/fresh_generation/weekly_etf_eu_review_260803_05.pdf
attachment_count=4
```

The client reports show:

- the three official positions and fresh NAV;
- six current promoted UCITS opportunities with current closing-price evidence;
- the retained VVSM Stage-1 line;
- the unexecuted VVSM/L0CK five-position model proposal;
- current blockers and authority boundaries;
- exact `L0CK` naming;
- the regime label explicitly identified as historical donor strategy context rather than a fresh EU regime calculation.

## PDF and visual review

```text
nl_pages=12
en_pages=11
total_rendered_pages=23
low_content_pages=0
minimum_nl_page_text_characters=936
minimum_en_page_text_characters=888
clipping=false
overlap=false
orphan_page=false
visual_review=passed_all_pages
```

Independent artifact inspection confirmed that the compact close/evidence column preserves all promoted ticker rows without the prior Dutch orphan-page spillover.

## Protected-state proof

```text
portfolio_state_sha256=6642334558818e630f0b22a2500ef44b2489ff237aacca638e81f184c165aa6f
trade_ledger_sha256=718f0681fe0d1162f9a91c34aa90489eb8566aecb06c12a1a2d9ad251be3e87c
protected_state_unchanged=true
portfolio_mutation=false
ledger_write=false
execution_authority=false
delivery_authority=false
```

No report email was sent and no delivery receipt or delivery manifest was created.

## Bookkeeping note

The generated auxiliary run-summary JSON calculated `funded_position_count=0` because it queried a non-existent top-level state field. This does not affect the report, valuation, pricing gate, package manifest or client validators, all of which reconcile to three official funded positions. The authoritative funded-position count for this run is `3`.

## Final determination

```text
fresh_report=PASS
current_closing_prices=PASS_13_OF_13
funded_pricing_consensus=PASS_3_OF_3
official_funded_positions=3
model_proposal_positions=5
model_proposal_applied=false
client_report_consistency=PASS
pdf_visual_review=PASS_23_PAGES
protected_state=UNCHANGED
email_delivery=NOT_ATTEMPTED
```
