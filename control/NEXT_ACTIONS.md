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
- Status: next
- Target output names:
  - `output/weekly_etf_eu_review_YYMMDD.md`
  - `output/weekly_etf_eu_review_nl_YYMMDD.md`
  - `output/weekly_etf_eu_review_YYMMDD.pdf`
  - `output/weekly_etf_eu_review_nl_YYMMDD.pdf`
- Done when: EU reports cannot be confused with U.S. weekly ETF reports.

### 11. Add no-U.S.-ETF-as-report-holding validator

- Owner: `[ASSISTANT]`
- Status: next
- Target file:
  - `tools/validate_etf_eu_output_contract.py`
- Done when: EU report markdown fails validation if U.S. ETF tickers appear as investable holdings rather than research proxies.

### 12. Add first Dutch-first EU report skeleton

- Owner: `[ASSISTANT]`
- Status: next
- Target file:
  - `runtime/render_etf_eu_report.py`
- Done when: the repo can generate a non-delivery cash-only EU report skeleton with UCITS/proxy disclosure.

---

## Phase 3 — UCITS pricing and reporting

### 13. Build initial UCITS candidate registry

- Owner: `[JOINT]`
- Status: planned
- Action:
  - identify candidate UCITS ETFs by theme;
  - verify ISIN, provider, trading line, exchange, trading currency, TER, UCITS status and KID status;
  - keep `investability_status=candidate_requires_verification` until checked.
- Done when: registry contains verified candidates ready for pricing tests.

### 14. Adapt pricing to UCITS exchange lines

- Owner: `[ASSISTANT]`
- Status: planned
- Action:
  - price exchange ticker + exchange + trading currency;
  - retain U.S. proxy pricing only as research benchmark input;
  - add provider symbol and exchange lineage.
- Done when: EU holdings price from UCITS trading lines, not U.S. proxies.

### 15. Build Dutch-first EU report renderer

- Owner: `[ASSISTANT]`
- Status: planned
- Action:
  - render Dutch report as primary client output;
  - mark U.S. proxies as research-only;
  - disclose UCITS / PRIIPs / trading line status.
- Done when: Dutch/EU report is client-native, not a translation of a U.S. investable-universe report.

### 16. Enable EU delivery only after validators pass

- Owner: `[JOINT]`
- Status: blocked until Phases 1-3 are complete
- Done when: EU validator stack passes and a real delivery manifest/receipt exists.
