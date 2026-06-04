# Weekly ETF EU — Data Source Metadata Policy

Date: 2026-06-04  
Repository: `market-predictions/weekly-etf-eu`

## Purpose

This file defines source metadata categories for the EU/UCITS pricing spine.

It is not an approval list and not a valuation-grade policy by itself. It records how pricing evidence sources are classified so later source selection and agreement-gate logic can reason from explicit metadata instead of hardcoded assumptions.

## Authority boundary

The metadata register does not:

```text
create valuation_grade=true rows
create funding authority
mutate portfolio state
promote candidates to fundable
render reports
generate PDFs
send email
create delivery receipts
```

Pricing adapters return typed evidence. A later agreement gate must decide whether evidence is valuation-grade, provisional or blocked.

## Current source-role register

| source_id | source_type | usage_mode | license_class | authority_tier | review_status | counts_for_market_close_agreement | valuation_candidate_eligible | Notes |
|---|---|---|---|---|---|---:|---:|---|
| `euronext_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | true | true | Venue-specific official discovery candidate; license/session details still require review. |
| `deutsche_boerse_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | true | true | Venue-specific official discovery candidate; license/session details still require review. |
| `boerse_frankfurt` | `exchange` | `diagnostic_cross_check` | `unknown` | `diagnostic_candidate_source` | `pending_license_review` | false | false | Undocumented/free endpoint; exchange-candidate evidence only until reviewed. |
| `stooq` | `data_vendor` | `diagnostic_cross_check` | `provider_free_personal` | `diagnostic_candidate_source` | `pending_coverage_review` | false | false | Provisional/cross-check source; explicit symbol mappings require coverage verification. |
| `yahoo_yfinance` | `connectivity` | `fallback_provisional` | `provider_free_personal` | `non_authoritative_connectivity_only` | `provisional` | false | false | Temporary connectivity/display fallback evidence only; not agreement-gate valuation-grade authority and not market-close agreement evidence. |
| `issuer_nav` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Reference/stale-check evidence only; not exchange market-close agreement evidence. |
| `blackrock_issuer_reference` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Product facts/NAV sanity-check reference, not trading-line close authority. |
| `twelve_data` | `data_vendor` | `diagnostic_cross_check` | `provider_paid` | `diagnostic_candidate_source` | `pending_coverage_review` | false | false | Diagnostic candidate until symbol/date/currency/session evidence and plan status are reviewed. |
| `issuer_factsheet` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Instrument facts and stale sanity checks only. |

## Yahoo/yfinance authority reconciliation

Yahoo/yfinance can help show that a trading-line symbol is reachable and can preserve provisional/display evidence, but it must not be counted by the agreement gate as independent completed-session market-close evidence and must not populate valuation-grade authority fields under the current policy.

```text
yahoo_yfinance.counts_for_market_close_agreement=false
yahoo_yfinance.valuation_candidate_eligible=false
yahoo_yfinance.authority_tier=non_authoritative_connectivity_only
```

## Open review questions

1. Confirm license and redistribution constraints for venue-specific official/free endpoints.
2. Review whether the Börse Frankfurt / Xetra endpoint can ever move beyond diagnostic candidate evidence.
3. Verify Stooq coverage and exact symbol mappings before any stronger role.
4. Keep Yahoo/yfinance as temporary connectivity/display fallback only unless a future decision log entry and validator-backed implementation explicitly changes its role.
5. Keep issuer NAV and factsheets reference-only unless a separate NAV-specific report surface is designed.
6. Review Twelve Data plan/source terms before any candidate valuation role.
