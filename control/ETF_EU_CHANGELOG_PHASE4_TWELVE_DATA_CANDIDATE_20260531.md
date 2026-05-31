# Weekly ETF EU Review OS — Phase 4 Twelve Data Candidate Source Changelog

**Date:** 2026-05-31  
**Repository:** `market-predictions/weekly-etf-eu`  
**Scope:** Integrate Twelve Data as candidate valuation evidence source without funding or valuation-grade promotion.

---

## Current issue

The Phase 4 valuation-pricing artifact was validated, but every row remained `valuation_grade_pending` because no live candidate valuation source was integrated.

The next controlled step is to test Twelve Data as a candidate source while keeping the valuation authority gate closed.

---

## Root cause

A data provider can return a close, but that alone is not enough for EU UCITS valuation authority.

A UCITS valuation-grade row still requires:

```text
ISIN + exchange line + trading currency + provider symbol + source + observed date + close + source lineage + completed-session evidence
```

So Twelve Data should first be captured as structured candidate evidence, not immediately accepted as final valuation authority.

---

## Files changed

```text
config/ucits_pricing_source_policy.yml
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
.github/workflows/send-weekly-etf-eu-report.yml
```

---

## Change summary

### 1. Source policy updated

Added Twelve Data candidate-source settings for:

```text
CSPX / London Stock Exchange / USD / expected Twelve Data exchange LSE
SXR8 / Xetra / EUR / expected Twelve Data exchange XETRA
```

Both lines remain:

```text
accept_as_valuation_grade: false
```

### 2. Valuation builder updated

`pricing/build_ucits_valuation_prices.py` now attempts a Twelve Data `time_series` request for each configured candidate line.

The result is written into each row as:

```text
twelve_data_candidate_evidence
```

This evidence may include:

```text
status
observed_date
close
currency
provider_exchange
currency_matches_expected
completed_session
raw_meta
```

But it does not populate the valuation authority fields unless the future policy explicitly promotes the row.

### 3. Validator tightened

`tools/validate_ucits_valuation_prices.py` now validates the controlled schema for `twelve_data_candidate_evidence` and enforces:

```text
accept_as_valuation_grade must remain false
valuation_grade_row_count must remain 0 under the current policy
portfolio_mutation=false
production_delivery=false
funding_authority=false
```

### 4. Workflow updated

The EU validation workflow now exposes both secret names to the valuation step:

```text
TWELVE_DATA_API_KEY
TWELVEDATA_API_KEY
```

This preserves compatibility with the existing U.S. baseline secret naming while allowing a clearer underscore-separated name.

---

## Expected validation behavior

If a Twelve Data secret is available and the symbols resolve, the artifact should show:

```text
twelve_data_candidate_evidence.status: candidate_price_observed
valuation_status: valuation_grade_pending
valuation_grade: false
valuation_grade_row_count: 0
```

If the secret is missing or the provider does not resolve the symbols, the workflow should still pass as long as the unresolved evidence is structured and non-authoritative.

---

## What this does not do

This change does **not**:

- fund any ETF;
- mutate EU portfolio state;
- write valuation history;
- enable PDF generation;
- enable email delivery;
- promote Twelve Data to final valuation authority;
- mark any UCITS candidate as fundable.

---

## Next action

Run EU bootstrap validation through a queue file and inspect the generated `output/pricing/ucits_valuation_prices_*.json` artifact to see whether Twelve Data returned candidate evidence for CSPX and SXR8.
