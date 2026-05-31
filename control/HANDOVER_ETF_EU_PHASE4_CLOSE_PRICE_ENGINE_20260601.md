# Handover — Weekly ETF EU Phase 4 Close Price Engine

**Date:** 2026-06-01  
**Repository:** `market-predictions/weekly-etf-eu`  
**Session scope:** Phase 4 UCITS valuation-pricing architecture, official-source discovery, and generic close-price engine scaffold.

---

## Fresh-chat start rule

In the next chat, start by reading from GitHub in this order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/HANDOVER_ETF_EU_PHASE4_CLOSE_PRICE_ENGINE_20260601.md
```

Then read only the minimum relevant execution files, most likely:

```text
config/ucits_pricing_source_policy.yml
pricing/close_engine/contracts.py
pricing/close_engine/engine.py
pricing/close_engine/adapters/euronext.py
pricing/close_engine/adapters/deutsche_boerse.py
tools/validate_ucits_close_observations.py
.github/workflows/send-weekly-etf-eu-report.yml
```

---

## Current issue

The EU/UCITS ETF repo needs a reliable closing-price mechanism for European-style ETFs.

The session started by trying to prove pricing for two known UCITS trading lines:

```text
CSPX / Euronext Amsterdam / XAMS / EUR / IE00B5BMR087-XAMS
SXR8 / Deutsche Boerse Xetra / XETR / EUR / IE00B5BMR087
```

However, the user correctly challenged that hard-coding two pages is not a generic price engine.

The architectural direction was therefore changed:

```text
source-specific page research
→ generic ISIN/trading-line/source-adapter close-price engine
```

---

## Root cause / architectural tension

European UCITS ETFs cannot be priced reliably from ticker strings alone.

A single UCITS fund can have:

- one ISIN;
- multiple exchange trading lines;
- multiple tickers;
- multiple trading currencies;
- multiple venue identifiers;
- multiple provider symbol formats.

So the final engine must not be:

```text
any ticker string in, guaranteed close price out
```

The correct model is:

```text
ISIN-first UCITS instrument
+ verified trading line
+ source-policy registry
+ reusable source adapter
→ standardized close observation with blockers
```

Key identity tuple:

```text
registry_id + isin + exchange + exchange_ticker + trading_currency + source_id + adapter_name
```

---

## Stable design decisions made

### 1. Twelve Data will not be upgraded

Twelve Data recognized some UCITS symbols, but CSPX/LSE time-series data was plan-gated and the user explicitly decided not to upgrade the Twelve Data plan.

Decision:

```text
Twelve Data = diagnostic only under current policy
```

Do not build the EU valuation engine around a Twelve Data paid-plan dependency.

### 2. Official exchange sources are preferred candidates

Preferred official-source candidates:

```text
Euronext Amsterdam / XAMS
Deutsche Boerse / Xetra / XETR
```

These are still candidate sources, not valuation authority.

### 3. Page-evidence layer is source research, not the final engine

The official page-evidence artifacts are useful for learning page structure and source labels, but they should not keep growing into a giant scraper.

Decision:

```text
Freeze page-evidence work as source research.
Move durable logic into pricing/close_engine adapters.
```

### 4. Generic close-price engine scaffold is now validated

A generic close-price engine scaffold now exists and writes:

```text
output/pricing/ucits_close_observations_YYYYMMDD_HHMMSS.json
```

This is now the correct path for future development.

### 5. No valuation authority yet

All current artifacts must preserve:

```text
valuation_authority=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
completed_session=false
```

The system may collect candidate evidence, but nothing may be promoted to valuation-grade until a separate promotion validator exists.

---

## Files added during this phase

### Control / contracts / changelogs

```text
control/UCITS_CLOSE_PRICE_ENGINE_CONTRACT_V1.md
control/ETF_EU_CHANGELOG_PHASE4_TWELVE_DATA_CANDIDATE_20260531.md
control/ETF_EU_CHANGELOG_PHASE4_TWELVE_DATA_SYMBOL_DISCOVERY_20260531.md
control/ETF_EU_CHANGELOG_PHASE4_OFFICIAL_SOURCE_SNAPSHOT_20260531.md
control/ETF_EU_CHANGELOG_PHASE4_OFFICIAL_PAGE_EVIDENCE_20260531.md
control/ETF_EU_CHANGELOG_PHASE4_PRICE_OBSERVATION_EVIDENCE_20260531.md
control/ETF_EU_CHANGELOG_PHASE4_CLOSE_PRICE_ENGINE_SCAFFOLD_20260531.md
```

### Pricing / source evidence

```text
pricing/discover_twelve_data_ucits_symbols.py
pricing/build_official_exchange_source_snapshot.py
pricing/build_official_exchange_page_evidence.py
```

### Generic close engine

```text
pricing/close_engine/contracts.py
pricing/close_engine/engine.py
pricing/close_engine/adapters/__init__.py
pricing/close_engine/adapters/euronext.py
pricing/close_engine/adapters/deutsche_boerse.py
```

### Validators

```text
tools/validate_ucits_twelve_data_symbol_discovery.py
tools/validate_official_exchange_source_snapshot.py
tools/validate_official_exchange_page_evidence.py
tools/validate_ucits_close_observations.py
```

---

## Important files changed

```text
control/SYSTEM_INDEX.md
config/ucits_pricing_source_policy.yml
pricing/build_ucits_valuation_prices.py
tools/validate_ucits_valuation_prices.py
.github/workflows/send-weekly-etf-eu-report.yml
```

`control/SYSTEM_INDEX.md` now includes a GitHub run-verification rule:

```text
After queueing a run, ChatGPT must build in a short pause, then poll GitHub/status/artifact commits before concluding pass/fail.
```

This was added because immediate GitHub checks often return no run even though the Actions UI later shows the run.

---

## Current workflow behavior

Workflow:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

The workflow is still bootstrap validation only.

It currently runs these relevant phases:

```text
Validate EU control/config files
Validate UCITS symbol registry and investability contract
Build and validate UCITS pricing candidates
Run non-authoritative UCITS pricing preflight
Build and validate UCITS valuation pricing artifact
Snapshot official exchange source candidates
Build official exchange page evidence
Build and validate generic UCITS close observations
Discover Twelve Data UCITS provider symbols
Validate EU cash-only state and no U.S. ETF holdings
Render EU candidate report skeleton
Validate EU output/report contracts
Confirm no delivery is attempted
Commit bootstrap report and pricing artifacts
```

No PDF generation, portfolio mutation, funding, production delivery, or email sending is enabled.

---

## Latest confirmed run state

### Run #18

GitHub Actions UI showed:

```text
Queue Deutsche Boerse adapter candidate close validation #18
Status: Success
Commit: 6a52e0723cdec24214d6398509ddef769e39fe56
```

Repo-output verification also confirmed a new persisted artifact commit:

```text
2e885e3a855d68d38d33515db487fdcda7de3e97
message: Persist Weekly ETF EU candidate report artifacts [skip ci]
created_at: 2026-05-31T21:45:44Z
```

Latest close-observations artifact from that run:

```text
output/pricing/ucits_close_observations_20260531_214535.json
```

---

## Latest close-observation result

The artifact contains two rows.

### 1. Euronext / CSPX / XAMS

Current status:

```text
adapter_name: euronext_live
observation_status: adapter_scaffold_pending_endpoint_integration
candidate_close: null
candidate_date: null
candidate_currency: null
completed_session: false
valuation_authority: false
```

Blockers:

```text
stable_euronext_quote_endpoint_not_integrated
candidate_close_not_parsed
candidate_date_not_verified
completed_session_not_verified
```

Interpretation:

Euronext page identity is proven and endpoint hints were seen earlier, but the stable quote endpoint has not been integrated into the adapter.

### 2. Deutsche Boerse / SXR8 / XETR

Current status:

```text
adapter_name: deutsche_boerse_live
observation_status: candidate_close_not_observed
parser_status: no_clean_close_candidate_found
candidate_close: null
candidate_date: null
candidate_currency: null
completed_session: false
valuation_authority: false
```

The parser found relevant page labels:

```text
Schlusspreis des letzten Handelstages
Handelswährung EUR
Letzter Preis
```

But it did not find a clean official close adjacent to the official close label.

Important diagnostic:

```text
last_price_numeric_candidates: [500.0]
```

The adapter did not promote `500.0` because it came from the `Letzter Preis` window, not the official close label, and the close-label window still contains noisy layout text such as trading hours and 52-week range.

This is correct conservative behavior.

---

## Current output contract

Current artifacts are evidence-only.

The generic close observation artifact must remain:

```text
schema_version: ucits_close_observations_v1
portfolio_mutation: false
production_delivery: false
funding_authority: false
valuation_authority: false
```

A row may eventually contain:

```text
candidate_close
candidate_date
candidate_currency
```

but until a completed-session/source/date/currency validator exists, it must still include blockers and remain non-authoritative.

---

## What not to do next

Do **not**:

- promote Deutsche Boerse `Letzter Preis` to official close;
- accept `500.0` just because it appears plausible;
- relax the validator to force a candidate close;
- scrape more broad page text inside `build_official_exchange_page_evidence.py`;
- re-center the design around two hard-coded ETF pages;
- use ticker-only lookup as valuation authority;
- mutate `output/etf_eu_portfolio_state.json`;
- write valuation history;
- enable PDF/email delivery;
- claim production delivery succeeded.

---

## Recommended next action

Continue inside the generic close engine.

### Next technical step

Improve source-specific adapter diagnostics and parsing, but keep authority blocked.

Recommended order:

1. **Deutsche Boerse adapter diagnostics**
   - Inspect page HTML/scripts for embedded quote data or API hints.
   - Identify whether the official close is loaded client-side via an endpoint.
   - Keep `candidate_close=null` unless the value is cleanly tied to `Schlusspreis des letzten Handelstages`.

2. **Euronext endpoint integration**
   - Use existing page-evidence hints:
     ```text
     currentPath
     baseUrlSearchQuote
     dynamic_quotes_display
     product_data
     Live quotes
     ```
   - Identify the stable quote endpoint behind Euronext product pages.
   - Do not parse broad navigation text.

3. **Generic adapter contract expansion**
   - Add a structured diagnostics object to `CloseObservation` if needed.
   - Keep all adapters behind the same interface.

4. **Candidate-close validator**
   - Allow candidate close evidence only when:
     ```text
     positive close
     candidate currency == trading currency
     source lineage present
     blocker still marks close as unverified
     completed_session=false until session validator exists
     ```

5. **Only later: valuation-grade promotion layer**
   - Separate script/validator after close observations.
   - Must verify completed session, observed date, currency, staleness, source authority, and source lineage.

---

## Suggested next files to inspect

```text
pricing/close_engine/adapters/deutsche_boerse.py
pricing/close_engine/adapters/euronext.py
pricing/close_engine/contracts.py
pricing/close_engine/engine.py
tools/validate_ucits_close_observations.py
output/pricing/ucits_close_observations_20260531_214535.json
output/pricing/ucits_official_exchange_page_evidence_20260531_214535.json
```

If the exact artifact timestamp changes in the repo, inspect the latest matching files instead.

---

## Session close checklist

### Update `control/CURRENT_STATE.md`

Recommended state update:

```text
Phase 4 generic UCITS close-price engine scaffold is validated. Euronext and Deutsche Boerse are now adapters behind a generic observation contract. Deutsche Boerse parser attempted candidate evidence but correctly kept candidate_close null because no clean official close was parsed adjacent to the official close label. All authority flags remain false.
```

### Update `control/NEXT_ACTIONS.md`

Recommended next action update:

```text
Continue with generic close-engine adapter implementation. First inspect Deutsche Boerse page scripts/API hints and Euronext quote endpoint hints. Do not expand page-evidence scraping. Keep all candidate closes non-authoritative until completed-session/date/currency/source-lineage validation exists.
```

### Add to `control/DECISION_LOG.md` if present

Recommended stable decision:

```text
EU UCITS pricing must be implemented as an ISIN/trading-line/source-adapter close-price engine. Page-specific scraping artifacts are source research only and must not become the final generic engine. Twelve Data remains diagnostic only; no Twelve Data plan upgrade will be used.
```

---

## Fresh-chat instruction

In the fresh chat, ask ChatGPT to continue from this handover and to start by reading:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/HANDOVER_ETF_EU_PHASE4_CLOSE_PRICE_ENGINE_20260601.md
```

Then continue with adapter-level implementation in `pricing/close_engine/`.
