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
- Status: done
- Target file:
  - `runtime/render_etf_eu_report.py`
- Done when: Dutch and English skeletons display candidate registry rows, investability status and non-authoritative pricing-preflight status while keeping portfolio state cash-only.

### 23. Add candidate-report validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_etf_eu_candidate_report.py`
- Done when: report fails if UCITS candidate rows are presented as funded holdings or if pricing-preflight status is presented as valuation authority.

### 24. Add candidate-report run validation

- Owner: `[ASSISTANT]`
- Status: done
- Result:
  - GitHub Actions passed;
  - candidate-aware Dutch and English reports were rendered;
  - EU output contract and candidate-report contract passed;
  - no portfolio mutation, no funding authority, no PDF, no email.

---

## Phase 4 — valuation-grade UCITS pricing authority

### 25. Add valuation-grade UCITS pricing authority contract

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `control/UCITS_VALUATION_PRICING_CONTRACT_V1.md`
- Result: distinction between connectivity preflight and valuation-grade pricing authority is explicit.

### 26. Define authoritative pricing source order per UCITS trading line

- Owner: `[JOINT]`
- Status: done for initial conservative policy
- Target file:
  - `config/ucits_pricing_source_policy.yml`
- Result:
  - `exchange_official` is preferred valuation source but not yet integrated;
  - `twelve_data` is candidate valuation source pending trading-line symbol/date/currency verification;
  - `issuer_factsheet` is reference/stale-check only;
  - `yahoo_yfinance` remains non-authoritative connectivity only.

### 27. Add valuation-grade pricing artifact builder

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `pricing/build_ucits_valuation_prices.py`
- Result: separate valuation-price artifact can be produced without mutating portfolio state.

### 28. Add valuation-grade pricing validator

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `tools/validate_ucits_valuation_prices.py`
- Result: validator blocks valuation-grade status unless source, date, close, currency, completed-session and source-lineage requirements are met.

### 29. Wire valuation artifact into EU workflow and validate

- Owner: `[ASSISTANT]`
- Status: done
- Target file:
  - `.github/workflows/send-weekly-etf-eu-report.yml`
- Result:
  - GitHub Actions passed;
  - `output/pricing/ucits_valuation_prices_20260531_133912.json` committed;
  - artifact contains 2 pending valuation rows and 0 valuation-grade rows;
  - no portfolio mutation, no funding authority, no PDF, no email.

### 30. Integrate first authoritative valuation data source

- Owner: `[JOINT]`
- Status: superseded by pricing-spine path
- Updated action:
  - do not integrate a single source directly into the valuation artifact as the next step;
  - first integrate the common `PriceSource` / `PriceResult` interface;
  - then integrate at least two adapters and an agreement gate;
  - only then wire agreement-gate output into valuation artifacts.

### 31. Decide promotion path from candidate to fundable

- Owner: `[JOINT]`
- Status: planned after agreement-gate valuation path exists
- Action:
  - define when `verified_candidate_not_funded` can become `fundable`;
  - include instrument verification, pricing authority, liquidity, spread, role, risk and portfolio concentration gates.

### 32. Build Dutch-first EU production report renderer

- Owner: `[ASSISTANT]`
- Status: planned after first report pricing surface and fundability contract
- Action:
  - render Dutch report as primary client output;
  - mark U.S. proxies as research-only;
  - disclose UCITS / PRIIPs / trading line status;
  - convert skeleton into full UCITS candidate and eventually funded-position report.
- Done when: Dutch/EU report is client-native, not a translation of a U.S. investable-universe report.

### 33. Enable EU delivery only after validators pass

- Owner: `[JOINT]`
- Status: blocked until valuation-source integration, funded-state contract and production output validators pass
- Done when: EU validator stack passes and a real delivery manifest/receipt exists.

---

## Phase 5 — parallel pricing-spine integration

### 34. Integrate M0 ground-clearing

- Owner: `[ASSISTANT]`
- Status: done
- Integrated PR:
  - `#1 — M0 ground-clearing: pin dependencies and document EU bootstrap workflow`
- Merge commit:
  - `c1476171606206d369190bf4c8cf126222a1e753`
- Result:
  - `README.md` added for EU bootstrap orientation;
  - `archive/README.md` added with quarantine notes;
  - `requirements.txt` pinned;
  - `.gitignore` added without blocking `control/run_queue` or `output/*` behavior;
  - `control/CHANGELOG.md` created after integration.
- Authority result:
  - no pricing authority changed;
  - no funding authority changed;
  - no portfolio mutation changed;
  - no production delivery, PDF generation or email behavior changed.

### 35. Integrate common pricing interface

- Owner: `[ASSISTANT]`
- Status: done
- Integrated PR:
  - `#3 — M1: Add common pricing interface`
- Merge commit:
  - `0c21629aa315f18a0ebceb0a301841d457d2a554`
- Target files:
  - `pricing/README.md`
  - `pricing/price_result_schema.py`
  - `pricing/source_selection.py`
  - `pricing/sources/__init__.py`
  - `pricing/sources/base.py`
  - `tests/test_pricing_interface.py`
  - `tests/fixtures/pricing/fake_price_rows.json`
- Result:
  - common typed `PriceSource` / `PriceResult` interface exists;
  - adapter contract is `PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult`;
  - no workflow, portfolio state or delivery behavior changed.

### 36. Integrate provider adapters after interface

- Owner: `[ASSISTANT]`
- Status: done
- Integrated PRs:
  1. `#4 — M1: Add Stooq pricing adapter` — `c92cff7a973f27f152b4c866515d7c84e28135d6`
  2. `#5 — M1: Add Börse Frankfurt / Xetra pricing adapter` — `34d6c909e87015de49e31ed3fc25294084faad16`
  3. `#6 — M1: Add Yahoo fallback pricing adapter` — `9138efd0d5613527bd6ab6f44313596e6cb6907f`
  4. `#7 — M1: Add issuer NAV reference adapter` — `7b74a36de88b8fdb5b4a4f8709312df533c27a9d`
- Result:
  - at least two adapters return normalized resolved or unresolved `PriceResult` rows;
  - tests are fixture-backed and network-free;
  - no adapter creates valuation-grade logic by itself;
  - no workflow, portfolio state, output/report, PDF, email or delivery behavior changed.

### 37. Integrate source metadata policy

- Owner: `[ASSISTANT]`
- Status: next
- Work package:
  - `control/work_packages/WP_M5_SOURCE_METADATA_POLICY_20260603.md`
- Expected branch:
  - `workstream/source-metadata-policy`
- Target files from work package:
  - `control/DATA_SOURCE_METADATA.md`
  - `control/CHANGELOG.md`
  - `pricing/source_metadata_policy.py`
  - `tests/test_source_metadata_policy.py`
- Done when:
  - source metadata categories align with `PriceResult` / `SourceLineage` fields;
  - source policy can deterministically classify or filter pricing evidence;
  - tests pass without network;
  - no workflow, portfolio state or delivery behavior changes.

### 38. Integrate agreement gate

- Owner: `[ASSISTANT]`
- Status: queued after source metadata policy; technically unblocked by adapter availability
- Work package:
  - `control/work_packages/WP_M1_AGREEMENT_GATE_INTEGRATION_20260603.md`
- Done when:
  - agreement gate can mark rows `valuation_grade`, `provisional`, or `blocked`;
  - valuation-grade requires configured source agreement conditions;
  - issuer NAV does not count as independent market-close agreement evidence;
  - Yahoo/yfinance is not the only route to valuation-grade status;
  - no result creates funding authority or portfolio mutation.

### 39. Integrate first report pricing surface

- Owner: `[ASSISTANT]`
- Status: blocked until agreement gate exists
- Work package:
  - `control/work_packages/WP_M2_FIRST_REPORT_INTEGRATION_20260603.md`
- Done when:
  - at least one verified UCITS candidate can display a real priced row when agreement-gate data exists;
  - report distinguishes priced candidates from funded holdings;
  - cash-only portfolio state remains unchanged;
  - no production delivery is created.

---

## Roadmap after control consolidation

1. Source metadata policy.
2. Agreement gate.
3. Valuation artifact integration with agreement output.
4. First report pricing surface.
5. Fundability / candidate-promotion contract.
6. Production Dutch-first report.
7. Delivery enablement only after validators and manifest/receipt path exist.

## Standing authority boundaries

Until a future decision log entry and validator-backed implementation explicitly change them:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

Adapters produce pricing evidence only. They do not mutate state, fund candidates, render reports, generate PDFs, send email or create delivery receipts.