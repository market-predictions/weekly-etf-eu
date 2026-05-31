# Weekly ETF EU Review OS — Phase 3 Candidate Report Changelog Addendum

**Date:** 2026-05-31  
**Scope:** Dutch-first UCITS candidate report surface.

---

## 2026-05-31 — Candidate registry table added to EU report renderer

### File changed

```text
runtime/render_etf_eu_report.py
```

### Commit

```text
5ff9b6e1599b5549d81015fe254d11f11371fca4
```

### Change

Extended the Dutch-first / English companion renderer so the non-delivery EU report now includes a UCITS candidate registry table.

### New report behavior

The report surfaces:

- candidate role;
- instrument name;
- ISIN;
- trading line;
- investability status;
- U.S. proxy labelled as research-only;
- non-authoritative pricing-preflight status;
- portfolio status explicitly stating the candidate is not funded and has no valuation authority.

### Authority rule

The candidate table is not a portfolio table, not a buy recommendation and not valuation authority.

---

## 2026-05-31 — Candidate-report validator added

### File added

```text
tools/validate_etf_eu_candidate_report.py
```

### Commit

```text
e144c5968e0fa73a2abafbd272d0ee5cd24c5d33
```

### Change

Added a validator that enforces the report-surface distinction between UCITS candidates and funded holdings.

### Validator checks

- Dutch report contains `UCITS-kandidatenregister`;
- English report contains `UCITS candidate registry`;
- report states candidate table is not a portfolio;
- report states candidate table is not a buy recommendation;
- report states candidate table is not valuation authority;
- candidate rows say not funded / no valuation authority;
- pricing-preflight status is described as non-authoritative connectivity only.

---

## 2026-05-31 — EU workflow now validates candidate-report layer

### File changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

### Commit

```text
b9f10776b16bfdfd73e8c151bdd86d7180e4a283
```

### Change

Updated the EU bootstrap workflow to pass the registry and pricing-preflight artifact into the renderer, then validate both the general EU output contract and the candidate-report contract.

### Still blocked

```text
no portfolio mutation
no funded holdings
no production PDF
no email delivery
```

---

## Next expected validation

Queue and run a fresh EU bootstrap validation request.

Expected markers include:

```text
ETF_EU_REPORT_RENDER_OK | candidate_registry=True
ETF_EU_OUTPUT_CONTRACT_OK
ETF_EU_CANDIDATE_REPORT_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```
