# ETF EU Review — Mature Bilingual Draft

## ETF EU mature draft status

```text
review_only=true
production_delivery=false
recipient_activation=false
send_attempted=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
```

This mature English draft is derived from EU source artifacts only. It is not a delivery artifact and does not create funding, valuation-grade, portfolio or recipient authority.

## Source artifact provenance

| Artifact | Path |
| --- | --- |
| Source draft report | `output/weekly_etf_eu_review_260618_draft.md` |
| UCITS pricing evidence | `output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json` |
| Donor-port comparison | `output/porting/etf_eu_wp14g_donor_comparison_20260618_000000.json` |
| Bilingual readiness gate | `output/bilingual/etf_eu_bilingual_surface_readiness_20260618_000000.json` |
| Delivery/PDF dry-run manifest | `output/delivery/etf_eu_delivery_pdf_dry_run_20260618_000000.json` |

Pricing evidence summary: prices_found=2, pricing_symbols_attempted=2, source_errors=0.

## 1. ETF EU Review — Draft status

```text
review_only=true
production_delivery=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
```

This is a review-only ETF EU markdown draft generated from UCITS identity and committed UCITS closing-price smoke evidence.

## 2. Executive summary

The EU repository has proven first live UCITS closing-price retrieval through the direct Yahoo chart endpoint for the first tested UCITS exchange-line symbols. The committed smoke artifact records 2 successful price rows, 2 attempted pricing symbols, 3 skipped pending symbols, and 0 source errors.

Yahoo chart pricing is source evidence only. It is not valuation-grade authority by itself, not funding authority, not portfolio mutation authority, and not delivery authority.

### EU decision cockpit

- **Draft status:** review-only; no production delivery or portfolio mutation.
- **Pricing basis:** UCITS exchange-line close evidence from the committed smoke artifact.
- **Main active boundary:** U.S. ETFs remain research proxies only, not EU investable holdings.
- **Next action trigger:** expand the EU report runtime and bilingual quality gates before any delivery dry run.

## 3. UCITS pricing evidence used

Pricing artifact used: `output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json`

| fund_name | isin | exchange_ticker | pricing_symbol | close_date | close | trading_currency | source_currency | source_exchange | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX | CSPX.L | 2026-06-17 | 809.239990234375 | USD | USD | LSE | yahoo_chart |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 | SXR8.DE | 2026-06-17 | 698.02001953125 | EUR | EUR | GER | yahoo_chart |

Source/freshness disclosure: the prices above come from the direct Yahoo chart endpoint as daily close evidence for UCITS exchange-line symbols. The report uses the latest non-null close present in the committed smoke artifact.

## 4. UCITS identity table

Registry used: `config/ucits_symbol_registry.yml`

| registry_id | fund_name | isin | exchange | exchange_ticker | trading_currency | pricing_symbol_yahoo | ucits_status | priips_kid_status | investability_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | London Stock Exchange | CSPX | USD | CSPX.L | confirmed | available | verified_candidate_not_funded |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | Xetra | SXR8 | EUR | SXR8.DE | confirmed | available | verified_candidate_not_funded |

## 5. Research proxy separation

U.S. ETFs are research proxies only and are not EU investable holdings.

| registry_id | fund_name | us_research_proxy | purpose |
| --- | --- | --- | --- |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | SPY | benchmark_reference_only |

SPY may be used only as benchmark reference or research comparator. It is not an EU holding in this report.

## 6. Initial observations

- The first two UCITS lines now have usable close evidence.
- The pricing source path is technically viable for the first tested UCITS exchange-line symbols.
- Further universe expansion is still needed before a broader EU report can be considered complete.
- The current evidence supports report-surface review only and does not create funding, portfolio, valuation-grade, or delivery authority.

## 7. Open gaps before production use

- Broader UCITS coverage.
- KID/PRIIPs validation across the investable universe.
- Liquidity, spread, exchange suitability and TER enrichment.
- Valuation-grade agreement gate and source policy promotion.
- Bilingual runtime port from the mature weekly-etf report path.
- Dutch language quality gate.
- Delivery/PDF dry run.
- Receipt/manifest path for any later production delivery claim.

## 8. Mature bilingual rendering next development step

```text
WP14J — ETF EU HTML/PDF render dry run from mature bilingual reports, no recipients
```

Delivery remains blocked. This package produces mature bilingual report surfaces only.

## 9. Authority and delivery disclaimer

This report is review-only. No production delivery occurred. No live send occurred. No recipient activation occurred. No portfolio mutation occurred. No candidate was promoted to fundable. Yahoo chart pricing is source evidence only and not valuation-grade authority by itself.
