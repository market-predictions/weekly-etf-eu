# Changelog — Phase 4 Yahoo UCITS Close Diagnostics

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: non-authoritative Yahoo/yfinance UCITS close diagnostics.

## Current issue

The Euronext dynamic-page path has not exposed a stable close-price endpoint. The repo already contains Yahoo/yfinance policy symbols for UCITS trading lines, but Yahoo must remain connectivity-only until symbol, currency, date, close and lineage are proven per trading line.

## Change

Added:

- pricing/build_yahoo_ucits_close_diagnostics.py
- tools/validate_yahoo_ucits_close_diagnostics.py

Updated:

- .github/workflows/send-weekly-etf-eu-report.yml
- tools/build_etf_eu_shadow_validation_evidence.py
- tools/validate_etf_eu_shadow_validation_evidence.py

## Behavior

The workflow now reads yahoo_yfinance entries from config/ucits_pricing_source_policy.yml and probes the configured Yahoo symbols such as CSPX.AS, CSPX.L and SXR8.DE.

The artifact records observed close/date/currency presence and mapping ambiguity flags. It deliberately does not mark any Yahoo row as unambiguous because ISIN is not verified in this diagnostic phase.

Expected output pattern:

- output/pricing/yahoo_ucits_close_diagnostics_YYYYMMDD_HHMMSS.json

## Safety posture

Yahoo/yfinance remains non-authoritative connectivity only. The artifact cannot create valuation authority, funding authority, candidate close extraction, completed-session validation, portfolio mutation, PDF generation, email delivery or delivery receipt.

## Next action

Queue the bootstrap workflow and inspect the Yahoo diagnostic artifact. If Yahoo returns recent closes with matching currency for CSPX.AS and SXR8.DE, compare it against Twelve Data and official-source evidence before considering any future policy revision.
