# Weekly ETF EU Review OS — Phase 4 Twelve Data Symbol Discovery Changelog

**Date:** 2026-05-31  
**Repository:** `market-predictions/weekly-etf-eu`  
**Scope:** Add diagnostic Twelve Data provider-symbol discovery after initial candidate-source probes returned HTTP 404.

---

## Current issue

The `Queue Twelve Data candidate source validation run #9` workflow passed, but the generated valuation artifact showed that Twelve Data did not resolve the configured symbols:

```text
CSPX / LSE
SXR8 / XETRA
```

Both returned structured evidence with:

```text
status: unresolved_provider_exception
error: HTTP Error 404: Not Found
```

The workflow and validator were healthy, but the provider-symbol assumption was not confirmed.

---

## Root cause

This is a provider-symbol discovery problem, not a portfolio or valuation-authority problem.

UCITS trading-line identity is known at the registry level, but Twelve Data may use a different identifier, exchange code, MIC code or search result convention than:

```text
CSPX + LSE
SXR8 + XETRA
```

We should discover provider identifiers before promoting any provider result to valuation-grade authority.

---

## Files changed

```text
config/ucits_pricing_source_policy.yml
.github/workflows/send-weekly-etf-eu-report.yml
```

## Files added

```text
pricing/discover_twelve_data_ucits_symbols.py
tools/validate_ucits_twelve_data_symbol_discovery.py
```

---

## Change summary

### 1. Candidate symbol probes added to policy

For CSPX London, added diagnostic probes:

```text
CSPX / LSE
CSPX / XLON
CSPX.L
CSPX:LN
IE00B5BMR087
```

For SXR8 Xetra, added diagnostic probes:

```text
SXR8 / XETRA
SXR8 / XETR
SXR8.DE
SXR8:GY
IE00B5BMR087
```

These are discovery probes only, not approved valuation identifiers.

### 2. Symbol-discovery artifact builder added

`pricing/discover_twelve_data_ucits_symbols.py` creates:

```text
output/pricing/ucits_twelve_data_symbol_discovery_YYYYMMDD_HHMMSS.json
```

It attempts:

```text
time_series
symbol_search
```

for each configured probe, and records HTTP/provider responses without failing the workflow when symbols do not resolve.

### 3. Symbol-discovery validator added

`tools/validate_ucits_twelve_data_symbol_discovery.py` validates artifact shape and confirms:

```text
portfolio_mutation=false
production_delivery=false
funding_authority=false
valuation_authority=false
```

The validator does not require a provider match. It only requires structured evidence.

### 4. Workflow wired

The EU workflow now runs symbol discovery after the valuation artifact step and commits:

```text
output/pricing/ucits_twelve_data_symbol_discovery_*.json
```

---

## Expected next validation behavior

The next workflow should pass if the discovery artifact is well-formed.

The key information to inspect after the run is:

```text
resolved_time_series_attempts
symbol_search_matches_found
```

If a probe resolves, the next implementation step is to update `config/ucits_pricing_source_policy.yml` with the confirmed Twelve Data provider identifier while keeping:

```text
accept_as_valuation_grade: false
```

until a separate promotion decision is made.

---

## What this does not do

This patch does not:

- fund any ETF;
- mutate portfolio state;
- approve Twelve Data as valuation authority;
- write valuation history;
- produce PDFs;
- send email.
