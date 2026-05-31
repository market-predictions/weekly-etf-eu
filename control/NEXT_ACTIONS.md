# Weekly ETF EU Review OS — Next Actions

## Status legend

- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = can be done directly in chat/repo
- `[JOINT]` = I prepare, you approve or verify

---

## Phase 0 — repo split

### 1. Confirm new repo exists

- Owner: `[USER]`
- Status: done
- Result: `market-predictions/weekly-etf-eu` was created and mirror-pushed from `market-predictions/weekly-etf`.

### 2. Preserve U.S. repo as baseline

- Owner: `[JOINT]`
- Status: standing rule
- Action: do not destructively change `market-predictions/weekly-etf` for EU/UCITS requirements.
- Done when: U.S. and EU products remain separated.

---

## Phase 1 — EU control and state separation

### 3. Rewrite control layer for EU authority

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `control/SYSTEM_INDEX.md`
  - `control/CURRENT_STATE.md`
  - `control/NEXT_ACTIONS.md`
- Done when: the repo clearly defines itself as the UCITS/Dutch-client environment.

### 4. Add UCITS authority contracts

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `control/UCITS_ETF_REVIEW_CONTRACT_V1.md`
  - `control/UCITS_INVESTABILITY_RULES.md`
  - `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md`
  - `control/UCITS_MIGRATION_PLAN.md`
- Done when: EU decision framework, investability, symbol identity and migration are explicit.

### 5. Add EU config stubs

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `config/etf_eu_discovery_universe.yml`
  - `config/ucits_symbol_registry.yml`
  - `config/ucits_benchmark_proxy_map.yml`
  - `config/nl_client_investability_rules.yml`
- Done when: UCITS discovery and proxy mapping are separated from the inherited U.S. universe.

### 6. Add cash-only EU state

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `output/etf_eu_portfolio_state.json`
  - `output/etf_eu_valuation_history.csv`
  - `output/etf_eu_trade_ledger.csv`
  - `output/etf_eu_recommendation_scorecard.csv`
- Done when: EU model has its own starting state and does not use U.S. holdings as current truth.

### 7. Add no-U.S.-ETF-as-EU-holding validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_no_us_etf_as_eu_holding.py`
- Done when: funded EU positions fail validation if they use U.S.-listed ETF tickers as holdings.

---

## Phase 2 — workflow and output isolation

### 8. Disable inherited production send path until EU contract is ready

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `.github/workflows/send-weekly-report.yml`
- Done when: inherited U.S. workflow no longer performs pricing, portfolio mutation, PDF generation or email delivery in the EU repo.

### 9. Add EU run queue and workflow naming

- Owner: `[ASSISTANT]`
- Status: done
- Target paths:
  - `control/run_queue/weekly_etf_eu_report_request_YYYYMMDD_HHMMSS.md`
  - `.github/workflows/send-weekly-etf-eu-report.yml`
- Done when: ChatGPT-triggered EU bootstrap validation uses separate names from U.S. runs.

### 10. Add EU output contract

- Owner: `[ASSISTANT]`
- Status: done
- Target files:
  - `control/ETF_EU_OUTPUT_CONTRACT_V1.md`
  - `output/weekly_etf_eu_review_YYMMDD.md`
  - `output/weekly_etf_eu_review_nl_YYMMDD.md`
- Done when: EU reports cannot be confused with U.S. weekly ETF reports.

### 11. Add no-U.S.-ETF-as-report-holding validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_etf_eu_output_contract.py`
- Done when: EU report markdown fails validation if U.S. ETF tickers appear as investable holdings rather than research proxies.

### 12. Add first Dutch-first EU report skeleton

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `runtime/render_etf_eu_report.py`
- Done when: the repo can generate a non-delivery cash-only EU report skeleton with UCITS/proxy disclosure.

### 13. Confirm EU output-contract validation passed

- Owner: `[USER]`
- Status: done
- Result: GitHub Actions validation passed and generated markdown skeletons were committed.

---

## Phase 3 — UCITS registry, pricing and reporting

### 14. Build initial UCITS candidate registry

- Owner: `[JOINT]`
- Status: done for bootstrap seed
- Target file:
  - `config/ucits_symbol_registry.yml`
- Result:
  - registry seeded with CSPX, VanEck Semiconductor UCITS placeholder, iShares Physical Gold ETC policy-blocked candidate, and infrastructure placeholder;
  - only CSPX is currently `verified_candidate_not_funded`;
  - no candidate is funded.

### 15. Add UCITS registry validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_ucits_symbol_registry.py`
- Done when: registry fails if required ISIN/trading-line/investability fields are missing or inconsistent.

### 16. Add UCITS investability validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_ucits_investability_contract.py`
- Done when: a candidate cannot become fundable without ISIN, UCITS status, PRIIPs/KID status, exchange line, trading currency and pricing symbol.

### 17. Confirm UCITS registry validation passed

- Owner: `[USER]`
- Status: done
- Result: GitHub Actions validation passed after YAML syntax fix.

### 18. Add UCITS pricing-line contract

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `control/UCITS_PRICING_LINE_CONTRACT_V1.md`
- Done when: pricing-line authority is explicit for UCITS exchange ticker + exchange + trading currency + provider symbol.

### 19. Add UCITS pricing candidate extractor

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `pricing/build_ucits_pricing_candidates.py`
- Done when: verified-but-not-funded UCITS trading lines can be extracted into a pricing candidate artifact without changing portfolio state.

### 20. Add UCITS pricing candidate validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_ucits_pricing_candidates.py`
- Done when: pricing tests are limited to registry-approved UCITS candidates and exclude U.S. proxy holdings.

### 21. Run first UCITS pricing-line preflight

- Owner: `[ASSISTANT]`
- Status: done
- Result:
  - GitHub Actions passed;
  - UCITS pricing candidate artifact built and validated;
  - non-authoritative pricing preflight artifact built and validated;
  - no portfolio mutation, no funding authority, no PDF, no email.

### 22. Extend Dutch-first EU report skeleton with UCITS candidate table

- Owner: `[ASSISTANT]`
- Status: next
- Target file:
  - `runtime/render_etf_eu_report.py`
- Done when: Dutch and English skeletons display candidate registry rows, investability status and non-authoritative pricing-preflight status while keeping portfolio state cash-only.

### 23. Add candidate-report validator

- Owner: `[ASSISTANT]`
- Status: next
- Target file:
  - `tools/validate_etf_eu_candidate_report.py`
- Done when: report fails if UCITS candidate rows are presented as funded holdings or if pricing-preflight status is presented as valuation authority.

### 24. Add candidate-report run validation

- Owner: `[ASSISTANT]`
- Status: planned
- Action:
  - wire candidate-report validator into `.github/workflows/send-weekly-etf-eu-report.yml`;
  - queue validation run;
  - keep delivery disabled.

### 25. Move toward valuation-grade UCITS pricing

- Owner: `[JOINT]`
- Status: planned after candidate-report validation
- Action:
  - define authoritative pricing source order for UCITS exchange lines;
  - decide whether Twelve Data, Yahoo, issuer factsheets or exchange data are valuation-grade per line;
  - retain yfinance as connectivity/research-grade until explicitly promoted.

### 26. Build Dutch-first EU production report renderer

- Owner: `[ASSISTANT]`
- Status: planned
- Action:
  - render Dutch report as primary client output;
  - mark U.S. proxies as research-only;
  - disclose UCITS / PRIIPs / trading line status;
  - convert skeleton into full UCITS candidate and eventually funded-position report.
- Done when: Dutch/EU report is client-native, not a translation of a U.S. investable-universe report.

### 27. Enable EU delivery only after validators pass

- Owner: `[JOINT]`
- Status: blocked until Phase 3/4 validates
- Done when: EU validator stack passes and a real delivery manifest/receipt exists.
