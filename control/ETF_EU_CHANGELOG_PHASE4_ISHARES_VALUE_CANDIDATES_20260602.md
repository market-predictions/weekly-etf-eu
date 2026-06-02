# Changelog — Phase 4 iShares Reference Value Candidates

Date: 2026-06-02
Repository: market-predictions/weekly-etf-eu
Scope: Non-authoritative issuer reference value-candidate artifact.

## Current issue

The iShares controlled parser probe showed stable selector candidates for cwpScreenerApi and productScreenerV3Api. The next safe step is to record label/selector candidates and context hashes without extracting NAV, price, date or currency values.

## Change

Added:

- pricing/build_ishares_reference_value_candidates.py
- tools/validate_ishares_reference_value_candidates.py

Updated:

- .github/workflows/validate-yahoo-fallback-gates.yml
- tools/build_yahoo_fallback_gate_shadow_evidence.py
- tools/validate_yahoo_fallback_gate_shadow_evidence.py

## Behavior

The dedicated Yahoo fallback gate workflow now builds a diagnostic value-candidate artifact for only:

- cwpScreenerApi
- productScreenerV3Api

The artifact records:

- candidate term labels such as ISIN, ticker, NAV, price, currency, date and fund name;
- selector/context hashes;
- nearby tag names;
- nearby attribute names;
- nearby class/id token samples;
- low/low-medium/medium confidence labels.

## Safety posture

This artifact is not value extraction. It stores no raw body samples and no NAV, price, date or currency values. It cannot pass the Yahoo fallback gate, cannot create valuation authority, cannot create funding authority, cannot mutate portfolio state, cannot generate PDF and cannot send email.

## Next action

Queue the dedicated Yahoo fallback gate workflow and inspect whether candidate coverage is good enough to design a separate value-extraction contract. Do not extract values without a new contract and validator.
