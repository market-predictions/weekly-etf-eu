# Handover — Weekly ETF EU Review OS — Phase 4 Valuation Pricing

**Repository:** `market-predictions/weekly-etf-eu`  
**Created:** 2026-05-31  
**Purpose:** Continue development in a fresh ChatGPT session without carrying over conversation bloat.  
**Current phase:** Phase 4 preparation — valuation-grade UCITS pricing authority.

---

## 0. Fresh-chat start sequence

In the fresh chat, start by reading from GitHub in this exact order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/HANDOVER_ETF_EU_PHASE4_VALUATION_PRICING_20260531.md
```

Then read only the minimum relevant execution files for the next task.

For Phase 4 valuation-pricing work, likely relevant files are:

```text
config/ucits_symbol_registry.yml
control/UCITS_PRICING_LINE_CONTRACT_V1.md
pricing/build_ucits_pricing_candidates.py
pricing/run_ucits_pricing_preflight.py
tools/validate_ucits_pricing_candidates.py
tools/validate_ucits_pricing_preflight.py
.github/workflows/send-weekly-etf-eu-report.yml
```

Do not start by editing the old U.S. repo or the inherited U.S. workflow.

---

## 1. Current issue

We created `market-predictions/weekly-etf-eu` as a clone of `market-predictions/weekly-etf`, then separated it into a Dutch/EU-client UCITS ETF review environment.

The system is now safe through the bootstrap/candidate-report stage, but it is not yet production-ready because pricing is still only a **non-authoritative connectivity preflight**.

The current stuck / next hard step is:

```text
move from non-authoritative UCITS pricing preflight to valuation-grade UCITS pricing authority
```

This must be done carefully. The previous U.S. ETF workflow had repeated pricing-state and equity-curve issues. Do not repeat that by letting a weak pricing source silently become portfolio valuation authority.

---

## 2. Root cause / architectural tension

The old `weekly-etf` repo was a U.S.-ETF model where ticker identity and U.S. pricing assumptions were more direct.

The EU repo has a different problem:

```text
UCITS ETF identity is ISIN-first, but pricing occurs at exchange trading-line level.
```

A single UCITS ETF can have multiple lines:

```text
same ISIN
multiple exchange tickers
multiple trading currencies
multiple provider symbols
```

So the EU pricing layer must not be ticker-first. It needs pricing authority at this level:

```text
ISIN + exchange + exchange_ticker + trading_currency + provider_symbol + pricing_source + observed_date + close + source_lineage
```

The current system already has a non-authoritative yfinance connectivity test. That test can prove symbols like `CSPX.L` or `SXR8.DE` may be reachable, but it must not become valuation authority automatically.

---

## 3. Stable design decisions already made

### Repo split

```text
market-predictions/weekly-etf = U.S.-ETF baseline
market-predictions/weekly-etf-eu = Dutch/EU-client UCITS ETF model
```

### Instrument authority

- U.S.-listed ETFs are **not** EU portfolio instruments.
- U.S. ETFs may appear only as research proxies / benchmark comparators.
- UCITS ETFs are the intended investable instruments.
- EU identity is ISIN-first.
- Ticker alone is not enough.

### Portfolio authority

- Current EU portfolio state is cash-only.
- No UCITS candidate is funded yet.
- Candidate visibility in the report is not portfolio authority.
- Pricing connectivity is not funding authority.

### Delivery authority

- Inherited U.S. production sender is disabled.
- EU workflow currently performs validation and artifact generation only.
- No production PDF.
- No email delivery.
- Do not claim delivery succeeded without a real manifest/receipt.

---

## 4. What is currently working

The latest GitHub Actions run shown by the user passed after the candidate-report layer was added.

Validated workflow stages include:

```text
Validate EU control files exist
Validate EU config files exist
Validate UCITS symbol registry and investability contract
Build and validate UCITS pricing candidates
Run non-authoritative UCITS pricing preflight
Validate EU cash-only state and no US ETF holdings
Render EU candidate report skeleton
Validate EU output and candidate report contracts
Validate inherited US production sender is disabled
Confirm no delivery is attempted
Commit EU bootstrap report and pricing preflight artifacts
```

The workflow is:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

The trigger path is:

```text
control/run_queue/weekly_etf_eu_report_request_*.md
```

---

## 5. Main files created/changed so far

### Control / authority files

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
control/UCITS_INVESTABILITY_RULES.md
control/UCITS_SYMBOL_REGISTRY_CONTRACT.md
control/UCITS_MIGRATION_PLAN.md
control/ETF_EU_OUTPUT_CONTRACT_V1.md
control/UCITS_PRICING_LINE_CONTRACT_V1.md
control/DECISION_LOG_EU.md
control/ETF_EU_CHANGELOG.md
control/ETF_EU_CHANGELOG_PHASE3_20260531.md
control/ETF_EU_CHANGELOG_PHASE3_PRICING_20260531.md
control/ETF_EU_CHANGELOG_PHASE3_CANDIDATE_REPORT_20260531.md
```

### Config files

```text
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
config/etf_eu_discovery_universe.yml
config/nl_client_investability_rules.yml
```

### EU state/output files

```text
output/etf_eu_portfolio_state.json
output/etf_eu_valuation_history.csv
output/etf_eu_trade_ledger.csv
output/etf_eu_recommendation_scorecard.csv
output/weekly_etf_eu_review_260531.md
output/weekly_etf_eu_review_nl_260531.md
output/pricing/ucits_pricing_candidates_*.json
output/pricing/ucits_pricing_preflight_*.json
```

### Runtime/pricing scripts

```text
runtime/render_etf_eu_report.py
pricing/build_ucits_pricing_candidates.py
pricing/run_ucits_pricing_preflight.py
```

### Validators

```text
tools/validate_no_us_etf_as_eu_holding.py
tools/validate_ucits_symbol_registry.py
tools/validate_ucits_investability_contract.py
tools/validate_ucits_pricing_candidates.py
tools/validate_ucits_pricing_preflight.py
tools/validate_etf_eu_output_contract.py
tools/validate_etf_eu_candidate_report.py
```

---

## 6. Current UCITS registry status

Current file:

```text
config/ucits_symbol_registry.yml
```

Seed entries:

```text
core_us_equity_cspx
semiconductor_vaneck_smh_ucits
gold_ishares_physical_gold_etc
infrastructure_ishares_global_infr
```

Current authority posture:

### `core_us_equity_cspx`

Status:

```text
verified_candidate_not_funded
```

Known lines:

```text
CSPX.L
SXR8.DE
```

This is currently the only registry entry eligible for non-authoritative pricing preflight.

### `semiconductor_vaneck_smh_ucits`

Status:

```text
candidate_requires_verification
```

Reason: visible ticker ambiguity and missing verification for domicile, distribution policy, replication method and pricing symbol.

Important: UCITS SMH may share ticker text with U.S. SMH in some contexts. Treat ISIN as authority, not ticker.

### `gold_ishares_physical_gold_etc`

Status:

```text
policy_review_required_not_ucits
```

Reason: iShares physical gold products are commonly ETCs, not UCITS ETFs. Do not fund under a UCITS-only policy unless policy explicitly changes.

### `infrastructure_ishares_global_infr`

Status:

```text
candidate_requires_verification
```

Reason: placeholder requiring issuer confirmation.

---

## 7. Current workflow behavior

Workflow:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

It currently:

1. installs Python dependencies;
2. resolves run id and report date;
3. validates EU control files;
4. validates EU config files;
5. validates UCITS registry and investability contract;
6. builds UCITS pricing candidates;
7. validates pricing candidates;
8. runs non-authoritative UCITS pricing preflight;
9. validates preflight artifact;
10. validates cash-only EU state and no U.S. ETF holdings;
11. renders Dutch-first and English companion candidate reports;
12. validates output and candidate-report contracts;
13. checks inherited U.S. sender is disabled;
14. confirms no delivery attempted;
15. commits report and preflight artifacts.

It currently does **not**:

```text
mutate portfolio state
mark candidates fundable
produce production PDF
send email
```

---

## 8. Current output contract

Current reports:

```text
output/weekly_etf_eu_review_260531.md
output/weekly_etf_eu_review_nl_260531.md
```

They are non-delivery candidate report skeletons.

The Dutch report is primary. The English report is companion/operator-facing during bootstrap.

The candidate table must clearly state:

```text
not a portfolio
not a buy recommendation
not valuation authority
not funded
U.S. proxies are research-only
pricing preflight is non-authoritative connectivity only
```

Validators enforcing this:

```text
tools/validate_etf_eu_output_contract.py
tools/validate_etf_eu_candidate_report.py
```

---

## 9. What not to do next

Do **not**:

- enable production email delivery;
- generate production PDFs;
- mark any candidate as `fundable`;
- mutate `output/etf_eu_portfolio_state.json` into holdings;
- treat yfinance output as valuation-grade pricing authority;
- treat U.S. ETFs as investable EU holdings;
- mechanically replace U.S. ETF tickers with UCITS tickers;
- overwrite the U.S. repo `market-predictions/weekly-etf`;
- remove the candidate/funding safeguards to get a green run.

---

## 10. Recommended next action in fresh chat

Start Phase 4 with design first, then code.

### Step 1 — Add valuation pricing contract

Create:

```text
control/UCITS_VALUATION_PRICING_CONTRACT_V1.md
```

It should define:

- difference between connectivity preflight and valuation-grade pricing;
- required price row fields;
- source authority hierarchy;
- close date / completed session rules;
- currency authority;
- stale price blocking rules;
- no portfolio mutation from pricing alone.

### Step 2 — Add pricing source policy config

Create:

```text
config/ucits_pricing_source_policy.yml
```

Suggested schema:

```yaml
schema_version: ucits_pricing_source_policy_v1
pricing_authority_mode: valuation_grade_pending
rules:
  portfolio_mutation_from_pricing: false
  yfinance_default_authority: non_authoritative_connectivity_only
  require_observed_date: true
  require_trading_currency_match: true
  require_source_lineage: true
  require_completed_market_session: true
sources:
  - source_id: twelve_data
    authority: candidate_valuation_source
    allowed_for:
      - exchange_ticker
      - provider_symbol
  - source_id: yahoo_yfinance
    authority: non_authoritative_connectivity_only
  - source_id: exchange_official
    authority: preferred_valuation_source
  - source_id: issuer_factsheet
    authority: reference_only_or_stale_check
```

### Step 3 — Add valuation artifact builder

Create:

```text
pricing/build_ucits_valuation_prices.py
```

It should read:

```text
config/ucits_symbol_registry.yml
config/ucits_pricing_source_policy.yml
output/pricing/ucits_pricing_candidates_*.json
```

It should write:

```text
output/pricing/ucits_valuation_prices_YYYYMMDD_HHMMSS.json
```

But in first version, it may set rows to:

```text
valuation_status: valuation_grade_pending
```

unless strict authority is available.

### Step 4 — Add valuation validator

Create:

```text
tools/validate_ucits_valuation_prices.py
```

It should fail if a row claims valuation-grade without:

```text
registry_id
isin
exchange
exchange_ticker
trading_currency
pricing_source
observed_date
close
currency
source_lineage
valuation_grade=true
completed_session=true
portfolio_mutation=false
funding_authority=false
```

### Step 5 — Wire into workflow as non-mutating phase

Update:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

Add valuation artifact build/validation after non-authoritative preflight, but keep:

```text
portfolio_mutation=false
funding_authority=false
delivery=false
```

### Step 6 — Queue validation run

Create:

```text
control/run_queue/weekly_etf_eu_report_request_YYYYMMDD_HHMMSS.md
```

Expected run markers should include:

```text
UCITS_VALUATION_PRICING_POLICY_OK
UCITS_VALUATION_PRICES_OK
UCITS_VALUATION_PRICES_VALIDATION_OK
ETF_EU_BOOTSTRAP_VALIDATION_ONLY
```

---

## 11. Suggested answer style in fresh chat

Use this structure:

```text
current issue
root cause
recommended change
exact file(s) to edit
next action
```

And always keep these four layers separate:

1. decision framework;
2. input/state contract;
3. output contract;
4. operational runbook.

---

## 12. Session close checklist after next work

At the end of the next meaningful session, update if needed:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_CHANGELOG.md or a dated changelog addendum
control/DECISION_LOG_EU.md if a stable architecture decision was made
```

Do not assume project files are updated unless GitHub writes actually succeeded.
