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

## Categories

### source_type

| Value | Meaning |
|---|---|
| `exchange` | Exchange or trading venue source candidate. |
| `data_vendor` | Data provider or aggregator. |
| `issuer` | Issuer-provided product/NAV/factsheet reference. |
| `connectivity` | Connectivity/fallback source that is useful operationally but not authority by itself. |
| `unknown` | Source type not yet reviewed. |

### usage_mode

| Value | Meaning |
|---|---|
| `official_close` | Candidate source for official or venue-specific completed-session close evidence. |
| `candidate_evidence` | Candidate valuation evidence requiring agreement-gate review. |
| `fallback_provisional` | Provisional fallback evidence; not sole valuation authority. |
| `diagnostic_cross_check` | Cross-check / diagnostic evidence only. |
| `reference_stale_check` | Issuer/reference/stale-check context, not exchange close evidence. |
| `connectivity_only` | Connectivity proof only. |

### authority_tier

Authority tiers must align with `pricing.price_result_schema`:

```text
exchange_official
candidate_valuation_source
diagnostic_candidate_source
non_authoritative_connectivity_only
unknown
```

These values describe evidence quality only. They do not create `valuation_grade=true` by themselves.

### review_status

| Value | Meaning |
|---|---|
| `reviewed` | Metadata reviewed for this role. |
| `provisional` | Useful but explicitly provisional. |
| `pending_license_review` | License/source-rights review still needed. |
| `pending_coverage_review` | Provider symbol or coverage still needs verification. |
| `reference_only` | Source is reference/stale-check only. |
| `unknown` | Review status is not known. |

## Current source-role register

| source_id | source_type | usage_mode | license_class | authority_tier | review_status | counts_for_market_close_agreement | valuation_candidate_eligible | Notes |
|---|---|---|---|---|---|---:|---:|---|
| `euronext_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | true | true | Venue-specific official discovery candidate; license/session details still require review. |
| `deutsche_boerse_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | true | true | Venue-specific official discovery candidate; license/session details still require review. |
| `boerse_frankfurt` | `exchange` | `diagnostic_cross_check` | `unknown` | `diagnostic_candidate_source` | `pending_license_review` | false | false | Undocumented/free endpoint; exchange-candidate evidence only until reviewed. |
| `stooq` | `data_vendor` | `diagnostic_cross_check` | `provider_free_personal` | `diagnostic_candidate_source` | `pending_coverage_review` | false | false | Provisional/cross-check source; explicit symbol mappings require coverage verification. |
| `yahoo_yfinance` | `connectivity` | `fallback_provisional` | `provider_free_personal` | `non_authoritative_connectivity_only` | `provisional` | false | false | Fallback/provisional evidence only; not the sole path to valuation-grade UCITS pricing. |
| `issuer_nav` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Reference/stale-check evidence only; not exchange market-close agreement evidence. |
| `blackrock_issuer_reference` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Product facts/NAV sanity-check reference, not trading-line close authority. |
| `twelve_data` | `data_vendor` | `diagnostic_cross_check` | `provider_paid` | `diagnostic_candidate_source` | `pending_coverage_review` | false | false | Diagnostic candidate until symbol/date/currency/session evidence and plan status are reviewed. |
| `issuer_factsheet` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | false | false | Instrument facts and stale sanity checks only. |

## Policy-mode helper semantics

The helper in `pricing/source_metadata_policy.py` filters metadata rows by declared policy mode.

| policy_mode | Intended use |
|---|---|
| `diagnostic_evidence` | Return all declared source metadata rows in input order. |
| `market_close_agreement_candidates` | Return only metadata rows that are allowed to count as market-close agreement candidates. |
| `valuation_candidate_evidence` | Return only rows flagged as valuation candidate evidence. |
| `reference_evidence` | Return issuer/reference/stale-check rows only. |

This is metadata filtering only. The agreement gate must still validate dates, closes, currencies, completed-session status, source lineage, agreement conditions and authority constraints.

## Open review questions

1. Confirm license and redistribution constraints for venue-specific official/free endpoints.
2. Review whether the Börse Frankfurt / Xetra endpoint can ever move beyond diagnostic candidate evidence.
3. Verify Stooq coverage and exact symbol mappings before any stronger role.
4. Decide whether Yahoo/yfinance remains diagnostic/fallback only or can be considered as provisional evidence under a future agreement-gate rule.
5. Keep issuer NAV and factsheets reference-only unless a separate NAV-specific report surface is designed.
6. Review Twelve Data plan/source terms before any candidate valuation role.
