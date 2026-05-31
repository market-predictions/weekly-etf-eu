# Weekly ETF EU Review OS — Phase 3 Changelog Addendum

**Date:** 2026-05-31  
**Scope:** UCITS candidate registry and investability validation bootstrap.

This addendum records Phase 3 material changes. It should be consolidated into `control/ETF_EU_CHANGELOG.md` during the next changelog maintenance pass if desired.

---

## 2026-05-31 — Initial UCITS candidate registry seeded

### File changed

```text
config/ucits_symbol_registry.yml
```

### Commit

```text
f64d6fdf6cb960577b10dda81e386f67ae341cc8
```

### Change

Replaced the empty bootstrap registry with an ISIN-first candidate registry.

### Candidates added

```text
core_us_equity_cspx
semiconductor_vaneck_smh_ucits
gold_ishares_physical_gold_etc
infrastructure_ishares_global_infr
```

### Authority posture

No candidate is funded.

The registry distinguishes:

- `verified_candidate_not_funded` for candidates that have enough issuer evidence to start pricing-line tests;
- `candidate_requires_verification` for placeholders requiring more evidence;
- `policy_review_required_not_ucits` for gold ETC exposure, because the iShares product is an ETC rather than a UCITS ETF.

### Important design decision

The VanEck Semiconductor UCITS ETF can share the visible ticker string `SMH` with U.S. semiconductor ETF contexts, so the EU model must remain ISIN-first. A ticker string alone is not sufficient authority.

---

## 2026-05-31 — UCITS symbol registry validator added

### File added

```text
tools/validate_ucits_symbol_registry.py
```

### Commit

```text
e7ffddc469ec776c0bf17ebf592e254fc06b1e96
```

### Change

Added a hard validator for `config/ucits_symbol_registry.yml`.

### Validator checks

- schema version is `ucits_symbol_registry_v1`;
- canonical identity is `isin_first`;
- registry IDs are present and unique;
- verified candidates have required fields such as ISIN, provider, UCITS/KID status, domicile, base currency, distribution policy, replication method, benchmark, TER and trading line data;
- U.S. proxy tickers are only accepted as research proxies;
- research proxies must carry `proxy_must_not_be_funded: true`;
- at least one verified candidate exists before the pricing phase begins.

---

## 2026-05-31 — UCITS investability contract validator added

### File added

```text
tools/validate_ucits_investability_contract.py
```

### Commit

```text
d6d518ab1d2e71647de6f2f7b5276b9998a8054e
```

### Change

Added a validator that prevents premature funding during the bootstrap phase.

### Validator checks

- no candidate may be marked `fundable` during bootstrap;
- fundable candidates, once later enabled, must be ETFs with confirmed UCITS status, KID availability, ISIN, provider, domicile, base currency, distribution policy, replication method, benchmark, TER and at least one complete trading line;
- ETCs or non-UCITS products must remain blocked unless policy is explicitly changed.

---

## 2026-05-31 — EU bootstrap workflow now validates UCITS registry

### File changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

### Commit

```text
d534a4847c8a3c3fe831016bd6587bf1b006a6cd
```

### Change

Added a PyYAML installation step and wired the new validators into the EU bootstrap workflow:

```text
python tools/validate_ucits_symbol_registry.py --registry config/ucits_symbol_registry.yml
python tools/validate_ucits_investability_contract.py --registry config/ucits_symbol_registry.yml
```

### Required behavior

The workflow should now validate the UCITS registry before rendering the non-delivery EU skeleton report.

It still performs:

```text
no pricing
no portfolio mutation
no PDF generation
no email delivery
```

---

## 2026-05-31 — UCITS registry YAML syntax fix

### Current issue

The first registry-validation run failed before semantic validation because the YAML parser hit an unquoted scalar containing markdown backticks in `bootstrap_notes`:

```text
- `verified_candidate_not_funded` means ...
```

Backticks can be problematic in plain YAML scalar contexts and should not appear unquoted inside operational config files.

### File changed

```text
config/ucits_symbol_registry.yml
```

### Commit

```text
6b2f50c8f3cc315790765c661a8299bedbbae2b6
```

### Change

- Quoted the bootstrap note that contains `verified_candidate_not_funded`.
- Demoted the VanEck Semiconductor UCITS entry from `verified_candidate_not_funded` to `candidate_requires_verification` because domicile, distribution policy, replication method and pricing symbol are still pending.
- Kept CSPX as the only `verified_candidate_not_funded` seed until more fields are verified for other candidates.

### Result expected

The next validation run should parse the registry successfully and proceed to semantic UCITS registry validation.

---

## Next expected validation

Queue and run a new EU bootstrap validation request. Expected new markers include:

```text
UCITS_SYMBOL_REGISTRY_OK
UCITS_INVESTABILITY_CONTRACT_OK
ETF_EU_OUTPUT_CONTRACT_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```
