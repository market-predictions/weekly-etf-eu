# Changelog — Phase 4 iShares Controlled Parser Probe

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Diagnostic controlled parser probe for iShares issuer reference endpoints.

## Current issue

The iShares endpoint structure probe showed that cwpScreenerApi and productScreenerV3Api expose HTML with useful labels and embedded structures, but no values should be extracted until stable selectors and parser shapes are understood.

## Change

Added:

- pricing/build_ishares_controlled_parser_probe.py
- tools/validate_ishares_controlled_parser_probe.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now builds a diagnostic controlled parser probe for only:

- cwpScreenerApi
- productScreenerV3Api

The probe records bounded parser-shape evidence:

- top tag counts;
- attribute-name samples;
- script attribute-name samples;
- class and id token samples;
- nearby tag/attribute shapes around ISIN, ticker, NAV, price, currency and date labels;
- whether a future controlled parser follow-up appears worthwhile.

## Safety posture

The parser probe is diagnostic-only. It does not store body samples, does not extract NAV, price, date or currency values, does not pass the Yahoo fallback gate, does not create valuation authority, does not create funding authority, does not mutate portfolio state, does not generate PDF and does not send email.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether the controlled parser probe finds stable selector candidates. If stable selectors exist, the next artifact can be a non-authoritative issuer reference value evidence artifact with strict extraction and validation gates.
