# Weekly ETF EU — Data Source Metadata Policy

Date: 2026-08-19  
Repository: `market-predictions/weekly-etf-eu`

## Current-status warning

This file is **source metadata**, not current production pricing authority.

The production pricing authority changed with merged PR #112 / main commit `5cc712582f86a51951cf57c55992f0ddc49a6ff1`. Use `control/PRICING_AUTHORITY_CURRENT.md` plus live merged runtime/tests for current behavior.

In particular, this file MUST NOT be read as requiring two live same-date sources for every funded position. That universal requirement is retired.

Current production rule in brief:

- one qualified provider, correctly bound to the canonical UCITS trading line, with the exact requested completed-session close can be valuation-grade as `fresh_exact_unverified`;
- an additional bound exact same-date source within tolerance upgrades the line to `fresh_exact_verified`;
- a stale/missing/unbound verifier does not invalidate a valid exact primary;
- actual same-date disagreement outside tolerance remains fail-closed;
- no exact close or identity/primary-binding mismatch remains fail-closed.

## Purpose

This register classifies source types and intended evidence roles. It does not select the live primary provider, define provider priority, create valuation-grade pricing by itself, create fundability or funding authority, or override current runtime qualification policy.

Provider names or roles recorded here may describe research, diagnostic or historical integration work. Current provider-symbol bindings and provider priority must be reconstructed from current code/config for the exact run.

## Authority boundary

The metadata register does not:

```text
create valuation_grade=true rows
require two providers for liveness
select a production primary provider
create funding authority
mutate portfolio state
promote candidates to fundable
render reports
generate PDFs
send email
create delivery receipts
```

Pricing adapters return typed evidence. Current qualification is performed by the merged primary+verification policy.

## Categories

### source_type

| Value | Meaning |
|---|---|
| `exchange` | Exchange or trading venue source candidate. |
| `data_vendor` | Data provider or aggregator. |
| `issuer` | Issuer-provided product/NAV/factsheet reference. |
| `connectivity` | Connectivity/fallback source useful operationally but not authority by itself. |
| `unknown` | Source type not yet reviewed. |

### usage_mode

| Value | Meaning |
|---|---|
| `official_close` | Candidate source for official or venue-specific completed-session close evidence. |
| `candidate_evidence` | Candidate valuation evidence subject to current qualification policy. |
| `fallback_provisional` | Provisional fallback evidence; not automatically production authority. |
| `diagnostic_cross_check` | Cross-check / diagnostic evidence only. |
| `reference_stale_check` | Issuer/reference/stale-check context, not exchange close evidence. |
| `connectivity_only` | Connectivity proof only. |

### authority_tier

```text
exchange_official
candidate_valuation_source
diagnostic_candidate_source
non_authoritative_connectivity_only
unknown
```

These values describe evidence quality only. They do not create `valuation_grade=true` by themselves and do not impose a two-source liveness rule.

### review_status

| Value | Meaning |
|---|---|
| `reviewed` | Metadata reviewed for this role. |
| `provisional` | Useful but explicitly provisional. |
| `pending_license_review` | License/source-rights review still needed. |
| `pending_coverage_review` | Provider symbol or coverage still needs verification. |
| `reference_only` | Source is reference/stale-check only. |
| `unknown` | Review status is not known. |

## Historical / research source-role register

The following table is retained as source-research provenance. It is **not** the current production provider allowlist or provider-priority table.

| source_id | source_type | usage_mode | license_class | authority_tier | review_status | Historical notes |
|---|---|---|---|---|---|---|
| `euronext_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | Venue-specific discovery candidate. |
| `deutsche_boerse_live` | `exchange` | `official_close` | `exchange_public` | `candidate_valuation_source` | `pending_license_review` | Venue-specific discovery candidate. |
| `boerse_frankfurt` | `exchange` | `diagnostic_cross_check` | `unknown` | `diagnostic_candidate_source` | `pending_license_review` | Diagnostic candidate only. |
| `stooq` | `data_vendor` | `diagnostic_cross_check` | `provider_free_personal` | `diagnostic_candidate_source` | `pending_coverage_review` | Historical cross-check candidate; verify mappings before use. |
| `yahoo_yfinance` | `connectivity` | `fallback_provisional` | `provider_free_personal` | `non_authoritative_connectivity_only` | `provisional` | Historical metadata classification; current Yahoo provider use, if any, is governed by current runtime/config binding rather than this row. |
| `issuer_nav` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | Reference/stale-check evidence only. |
| `blackrock_issuer_reference` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | Product facts/NAV sanity check only. |
| `twelve_data` | `data_vendor` | `diagnostic_cross_check` | `provider_paid` | `diagnostic_candidate_source` | `pending_coverage_review` | Diagnostic/research provenance only. |
| `issuer_factsheet` | `issuer` | `reference_stale_check` | `issuer_public` | `diagnostic_candidate_source` | `reference_only` | Instrument facts and stale sanity checks only. |

## Current authority pointers

For current production pricing behavior inspect:

- `control/PRICING_AUTHORITY_CURRENT.md`
- `config/ucits_symbol_registry.yml`
- `pricing/ucits_provider_identity_binding.py`
- `pricing/ucits_price_qualification_policy.py`
- `pricing/ucits_primary_verification_legacy.py`
- `pricing/build_ucits_close_price_validation_basket_results.py`
- `pricing/ucits_close_price_validation_contract_v2.py`
- current provider registry/config used by the runtime
- exact tests for the current report candidate

## Historical interpretation rule

Older documents may legitimately contain terms such as `two-provider consensus`, `market_close_agreement_candidates`, or `require-funded-consensus`. Treat them by lifecycle and date. After PR #112, compatibility naming does not mean that two simultaneous live providers are universally required for valuation-grade funded pricing.
