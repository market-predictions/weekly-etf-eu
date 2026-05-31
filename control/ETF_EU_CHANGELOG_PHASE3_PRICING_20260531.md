# Weekly ETF EU Review OS — Phase 3 Pricing Changelog Addendum

**Date:** 2026-05-31  
**Scope:** UCITS pricing-line candidate extraction and non-authoritative pricing preflight.

---

## 2026-05-31 — UCITS pricing-line contract added

### File added

```text
control/UCITS_PRICING_LINE_CONTRACT_V1.md
```

### Commit

```text
ae3b3a69d09a6a213f4d5e183e22c734596f6aff
```

### Change

Added the authority contract for UCITS pricing-line preflight.

### Key rules

- Pricing preflight tests market-data connectivity only.
- Pricing success cannot promote a candidate to `fundable`.
- Only registry entries with `investability_status: verified_candidate_not_funded` can enter the first preflight.
- U.S. ETF proxies are excluded from EU pricing candidates.
- Artifacts must state `portfolio_mutation: false`, `production_delivery: false`, and `funding_authority: false`.

---

## 2026-05-31 — UCITS pricing candidate extractor added

### File added

```text
pricing/build_ucits_pricing_candidates.py
```

### Commit

```text
d33dddeeb17a74a4b1cbfadd997b85f57276112d
```

### Change

Added a registry-driven extractor that writes:

```text
output/pricing/ucits_pricing_candidates_YYYYMMDD_HHMMSS.json
```

### Behavior

The extractor includes only verified-but-not-funded UCITS candidates with complete trading-line metadata.

Current expected eligible lines are CSPX/SXR8 from `core_us_equity_cspx`.

---

## 2026-05-31 — UCITS pricing candidate validator added

### File added

```text
tools/validate_ucits_pricing_candidates.py
```

### Commit

```text
8d22b21ef8cb423d2ae3db58792998e1fcf48edb
```

### Change

Added validation for the pricing-candidate artifact.

### Validator checks

- artifact schema is `ucits_pricing_candidates_v1`;
- top-level authority flags are false;
- every candidate has ISIN, provider, trading line, pricing symbol and investability metadata;
- candidates are only `verified_candidate_not_funded`;
- exchange ticker may not equal the U.S. research proxy ticker;
- duplicate registry/pricing-symbol pairs are blocked.

---

## 2026-05-31 — Non-authoritative UCITS pricing preflight added

### File added

```text
pricing/run_ucits_pricing_preflight.py
```

### Commit

```text
b3ff8e1fca7077d5716f4693a827db147a205e5d
```

### Change

Added a non-authoritative pricing connectivity test that attempts to fetch recent price history for candidate Yahoo-style symbols such as:

```text
CSPX.L
SXR8.DE
```

### Important authority rule

The output is not valuation authority. It is only a pricing-line connectivity preflight.

---

## 2026-05-31 — UCITS pricing preflight validator added

### File added

```text
tools/validate_ucits_pricing_preflight.py
```

### Commit

```text
12087c74e36c21a25d4ad7e3c1cf2da1f73321bd
```

### Change

Added validation for the non-authoritative pricing preflight artifact.

### Allowed result statuses

```text
priced_non_authoritative
unpriced_dependency_missing
unpriced_no_history
unpriced_provider_error
```

The validator does not require a live price by default, because provider/network issues should not mutate portfolio state or break the structural bootstrap unless explicitly requested later.

---

## 2026-05-31 — EU bootstrap workflow wired to pricing-line preflight

### File changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

### Commit

```text
ab78ccc3d4655087ba80dfb6a74b09d96477b56e
```

### Change

The EU bootstrap workflow now:

1. validates registry and investability;
2. builds UCITS pricing candidates;
3. validates pricing candidates;
4. runs non-authoritative UCITS pricing preflight;
5. validates preflight artifact;
6. validates cash-only EU state;
7. renders the non-delivery skeleton;
8. validates output contract;
9. commits markdown and pricing-preflight artifacts.

### Still explicitly blocked

```text
no portfolio mutation
no funded holdings
no production PDF
no email delivery
```

---

## Next expected validation

Queue and run a fresh EU bootstrap validation request.

Expected new markers include:

```text
UCITS_PRICING_CANDIDATES_OK
UCITS_PRICING_CANDIDATES_VALIDATION_OK
UCITS_PRICING_PREFLIGHT_OK
UCITS_PRICING_PREFLIGHT_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```
