# Weekly ETF EU Review OS — Changelog

**Repository:** `market-predictions/weekly-etf-eu`  
**Source baseline:** `market-predictions/weekly-etf`  
**Purpose:** Central log of material changes during the EU / Dutch-client UCITS ETF review migration.

This changelog records implementation changes. Stable architecture decisions are also summarized in `control/DECISION_LOG_EU.md`.

---

## 2026-05-30 — Repository split and EU/UCITS bootstrap started

### Current issue

The original `weekly-etf` repo had become a stable U.S.-ETF model with bilingual English/Dutch reporting, but the Dutch report still used U.S.-listed ETF instruments. Dutch/EU retail clients generally need UCITS / PRIIPs-compatible instruments, so a simple translation or ticker substitution would be structurally wrong.

### Change

Created the new repo:

```text
market-predictions/weekly-etf-eu
```

by mirror-pushing the existing `market-predictions/weekly-etf` history into a separate repository.

### Design intent

- `weekly-etf` remains the U.S.-ETF model baseline.
- `weekly-etf-eu` becomes the European / Dutch-client UCITS ETF model.
- U.S. ETFs may appear only as research proxies / benchmark references in the EU repo.
- UCITS ETFs become the investable instruments.
- EU instrument identity moves toward ISIN-first, not ticker-first.

---

## 2026-05-30 — EU control layer rewritten

### Files changed

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

### Change

Rewrote the inherited U.S.-ETF control layer so the repo clearly identifies itself as the EU/UCITS environment.

### Result

The EU repo now uses the following read order for meaningful work:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

and defines the four required layers:

1. decision framework;
2. input/state contract;
3. output contract;
4. operational runbook.

### Authority rules added

- Do not present U.S.-listed ETFs as investable holdings for Dutch/EU retail clients.
- U.S. ETFs are research proxies only.
- UCITS ETFs require ISIN-first identity.
- UCITS / PRIIPs / KID / trading-line verification is required before funding.
- EU production delivery is blocked until EU validators pass.

---

## 2026-05-30 — UCITS authority contracts added

### Files added

```text
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
control/UCITS_INVESTABILITY_RULES.md
control/UCITS_SYMBOL_REGISTRY_CONTRACT.md
control/UCITS_MIGRATION_PLAN.md
```

### Change

Added explicit authority documents for the EU/UCITS product.

### Material rules introduced

- The EU review asks: which UCITS ETFs available to Dutch/EU investors deserve capital?
- U.S.-listed ETFs are not portfolio instruments in this repo.
- A funded EU holding must have an ISIN and verified investability metadata.
- The symbol registry separates fund/share-class identity, exchange trading line, provider pricing symbol, U.S. research proxy and benchmark index.
- The migration will proceed in phases rather than a big-bang rewrite.

---

## 2026-05-30 — EU config stubs added

### Files added

```text
config/etf_eu_discovery_universe.yml
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
config/nl_client_investability_rules.yml
```

### Change

Created conservative bootstrap config files for UCITS discovery and Dutch/EU investability.

### Important implementation detail

The UCITS registry starts empty / conservative. Candidate mappings are marked as requiring verification rather than fundable. This avoids accidentally treating U.S. ETF proxies or unverified UCITS tickers as investable holdings.

### Proxy-map behavior

U.S. proxies such as SPY, SMH, GLD and PAVE are allowed only as research references that map to future UCITS candidates.

---

## 2026-05-30 — EU cash-only state added

### Files added

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
```

### Change

Added a separate EU state namespace and started the EU model as cash-only:

```text
cash_eur = 100000.0
invested_market_value_eur = 0.0
positions = []
```

### Reason

The cloned U.S. portfolio state must not become EU current-position truth. The EU model should only fund positions after UCITS instrument verification.

---

## 2026-05-30 — First EU holding validator added

### File added

```text
tools/validate_no_us_etf_as_eu_holding.py
```

### Change

Added a hard validator that blocks U.S.-listed ETF proxy tickers from funded EU holdings.

### Current checks

The validator fails if:

- a funded EU position uses U.S. proxy tickers such as SPY, QQQ, SMH, GLD, GSG, PPA, PAVE, URNM and related inherited proxy names;
- a non-cash funded position has no ISIN;
- a non-cash funded position is not marked as fundable / verified fundable.

### Result

The cash-only EU bootstrap state passes this validator.

---

## 2026-05-30 — Inherited U.S. production send workflow disabled

### File changed

```text
.github/workflows/send-weekly-report.yml
```

### Commit

```text
f16395b5345e9f49336839d210e660800d25875a
```

### Change

Disabled the inherited U.S.-ETF production workflow in the EU repo.

### Reason

The mirror clone copied a full U.S.-ETF production workflow that could run U.S. pricing, model execution, PDF rendering and email delivery. That is unsafe in the EU repo before the UCITS output contract exists.

### Result

The inherited workflow now only prints a disabled-workflow message and performs:

```text
no pricing
no portfolio mutation
no PDF rendering
no email delivery
```

---

## 2026-05-30 — EU bootstrap validation workflow added

### File added

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

### Commit

```text
588c56e2fa7470002f32cbac14758b9fef8bb9a4
```

### Change

Added an EU-only bootstrap validation workflow triggered by:

```text
control/run_queue/weekly_etf_eu_report_request_*.md
```

### Current workflow scope

This is validation-only. It checks:

- EU control files exist;
- EU config files exist;
- EU cash-only state exists;
- no U.S. ETF appears as an EU holding;
- inherited U.S. production sender is disabled;
- no delivery is attempted.

### Explicit non-goals

The workflow does not yet:

- run pricing;
- mutate portfolio state;
- generate PDF reports;
- send email.

---

## 2026-05-30 — First EU bootstrap validation run queued and passed

### File added

```text
control/run_queue/weekly_etf_eu_report_request_20260530_210000.md
```

### Commit

```text
58365d612ed241d71c9216aaa25681c39a1c0670
```

### Result

The first GitHub Actions run for `Weekly ETF EU UCITS bootstrap validation` passed.

### Validated markers

```text
ETF_EU_CONTROL_FILES_OK
ETF_EU_CONFIG_FILES_OK
EU_UCITS_HOLDING_VALIDATION_OK
ETF_EU_CASH_ONLY_STATE_OK
ETF_EU_INHERITED_SEND_DISABLED_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```

### Important note

This is not a production report delivery. It is only a bootstrap safety validation.

---

## 2026-05-30 — EU state and next actions updated after successful validation

### Files changed

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

### Commits

```text
20eb89f36cde96d5d6f80aeb67e3b641f150ab93
5a55f4a263074d22b4cbaaf9167046b366329f52
```

### Change

Recorded that the first EU bootstrap validation passed and advanced the next-action focus away from bootstrap isolation toward EU output-contract work.

### New next focus

```text
EU output contract
no-U.S.-ETF-as-report-holding validator
first Dutch-first EU report skeleton
UCITS candidate registry
```

---

## 2026-05-30 — EU decision log added

### File added

```text
control/DECISION_LOG_EU.md
```

### Commit

```text
f9b4a90af2230c54627f50dd780931dec95609cd
```

### Change

Created a separate decision log for stable EU architecture decisions.

### Distinction from this changelog

- `control/DECISION_LOG_EU.md` records stable architecture decisions.
- `control/ETF_EU_CHANGELOG.md` records material implementation changes.

---

## 2026-05-30 — EU output contract and report skeleton added

### Files added

```text
control/ETF_EU_OUTPUT_CONTRACT_V1.md
runtime/render_etf_eu_report.py
tools/validate_etf_eu_output_contract.py
```

### Workflow changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

### Commits

```text
fd27e661eb2321b6d902e318e0d14640b60ed800
c6d7f881e79ceb6ff07a9a13a256d94e0742bdcb
106aff730cb7242a6704463af3e3cfe6b6a48d18
c2a222fbd42477ea849853b7af897f36625f7f35
```

### Change

Added the first EU output contract and a Dutch-first cash-only report skeleton renderer.

The renderer creates:

```text
output/weekly_etf_eu_review_YYMMDD.md
output/weekly_etf_eu_review_nl_YYMMDD.md
```

### Required report wording

The skeleton must state:

```text
Current state: cash-only bootstrap
No UCITS holdings funded yet
U.S. ETFs are research proxies only
UCITS candidates require ISIN / KID / trading-line verification
Production delivery is disabled
```

The Dutch report communicates the same contract in Dutch and is treated as the primary EU client-facing output.

### Validator behavior

`tools/validate_etf_eu_output_contract.py` validates:

- EU-specific filenames;
- English companion and Dutch primary outputs both exist;
- U.S. ETF tickers appear only in proxy / benchmark / research-only context;
- required cash-only / no-funded-UCITS / no-delivery wording is present;
- inherited U.S. report names do not leak into the EU report body.

### Workflow behavior

The EU bootstrap workflow now:

1. validates control/config/state;
2. renders the EU cash-only markdown skeleton;
3. validates the EU output contract;
4. confirms inherited U.S. sender remains disabled;
5. confirms no pricing, portfolio mutation, PDF generation or email delivery is attempted;
6. commits generated EU markdown report skeletons back to `output/`.

### Important note

This is still non-delivery. No PDF or email is produced.

---

## Current status after this changelog update

The EU repo is safely separated at control/state/config/workflow level and now has a first non-delivery EU report output surface.

Production delivery remains blocked.

The next material implementation step should be:

```text
run EU bootstrap validation
inspect generated weekly_etf_eu_review_nl_*.md and weekly_etf_eu_review_*.md
then begin UCITS registry population with verified ISIN/trading-line candidates
```
