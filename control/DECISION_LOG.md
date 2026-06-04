# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-06-04 — ETF EU agreement-aware pricing-surface authority decisions

### Decision

The `market-predictions/weekly-etf-eu` repo may expose agreement-gate pricing evidence in a non-production report surface, but that evidence is not portfolio authority, not funding authority, not delivery authority and not a candidate-promotion mechanism.

The shadow workflow is created but must remain **pending verification** until GitHub Actions status or a committed validation artifact proves success.

### Chosen architecture

```text
source metadata policy
→ agreement gate
→ agreement-aware valuation wrapper
→ evidence-only pricing surface
→ fundability promotion contract
→ non-production shadow workflow
→ main workflow wrapper switch only after shadow verification
→ Dutch-first production report only after wrapper path is validated
→ delivery only after validators and receipt/manifest path exist
```

### Stable authority rules

1. Source metadata classifies source roles; it does not approve prices.
2. Agreement gate classifies evidence as `valuation_grade`, `provisional`, or `blocked`; it does not fund instruments or mutate portfolio state.
3. Agreement-aware valuation bridge may attach `agreement_gate_evidence`, but current bootstrap policy still preserves `valuation_grade=false` and `valuation_grade_row_count=0`.
4. The pricing-surface wrapper may display evidence in the Dutch/English report surface, but must explicitly avoid funded-holding, buy-recommendation or valuation-authority claims.
5. Fundability requires explicit non-price gates and a separate decision. No candidate can be auto-promoted from pricing success or report visibility.
6. Yahoo/yfinance may be temporary connectivity/display evidence, but not agreement-gate valuation-grade authority by itself.
7. Issuer NAV is reference/stale-check evidence only and does not count as independent market-close agreement evidence.
8. Shadow workflow creation is not the same as shadow workflow verification.
9. Production delivery cannot be claimed without a real receipt or manifest from the delivery layer.

### Reason

The EU/UCITS product needs deterministic evidence collection and visible report-surface progress, but client-grade valuation/funding/delivery authority must remain gated. A free/public provider or a displayed pricing surface must not silently become portfolio authority.

### Consequence

Current completed items:

```text
PR #8 source metadata policy
PR #9 agreement gate
PR #10 agreement-aware valuation bridge
pricing-surface wrapper
fundability promotion contract
shadow workflow created
```

Current pending items:

```text
shadow workflow verification
main workflow wrapper switch
production Dutch-first report
delivery enablement
```

Standing authority boundaries remain:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

---

## 2026-06-04 — Weekly ETF EU M1 pricing-spine authority decisions

### Decision

The `market-predictions/weekly-etf-eu` repo now has a typed multi-source pricing evidence spine, but adapter evidence is not valuation authority by itself.

### Chosen architecture

```text
PriceSource.fetch_eod_close(request: PriceRequest) -> PriceResult
```

The M1 pricing spine uses:

- `PriceIdentity`
- `PriceRequest`
- `PriceResult`
- `SourceLineage`
- shared status constants
- shared license-class constants
- shared authority-tier constants
- fixture-backed provider adapters returning typed resolved or unresolved rows

Stable source-role decisions:

- Yahoo/yfinance is fallback/provisional evidence only and must not be the sole path to valuation-grade UCITS pricing.
- Issuer NAV is reference/stale-check evidence only, not an exchange market-close source and not an independent market-close agreement source.
- Stooq is provisional / cross-check evidence until provider coverage and source policy allow stronger use.
- Börse Frankfurt / Xetra is exchange-candidate evidence only while the free endpoint remains undocumented and pending source/license review.
- Valuation-grade pricing requires source policy plus agreement gate conditions.
- Pricing adapters return evidence only; they do not mutate portfolio state, promote candidates, render reports, generate PDFs, send email, or produce delivery receipts.

### Reason

European UCITS pricing needs deterministic evidence collection before any valuation-grade, portfolio or delivery authority exists. A single free/public provider should not silently become the authority for client-facing valuation. The adapter layer therefore normalizes evidence; a later source metadata policy and agreement gate decide whether that evidence is valuation-grade, provisional or blocked.

### Consequence

The immediate roadmap after M1 pricing-spine integration was:

```text
source metadata policy
→ agreement gate
→ valuation artifact integration with agreement output
→ first report pricing surface
→ fundability / candidate promotion contract
→ Dutch-first production report
→ delivery enablement only after validators and receipt/manifest path exist
```

Standing authority boundaries remain:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```

---

## 2026-03-28 — Adopt Project + GitHub + Actions architecture

### Decision

The ETF flow will no longer be treated conceptually as one giant prompt-centered system.

### Chosen architecture

- **ChatGPT Project** = working memory and recurring workspace
- **GitHub repo** = explicit source of truth for prompts, scripts, outputs, and control docs
- **GitHub Actions + scripts** = real execution and delivery layer
- **Optional Custom GPT** = architect/reviewer only, not the primary runtime container

### Reason

This separates thinking/work context, system state/audit trail, and production execution.

---

## 2026-04-17 — Replace fixed structural-lane gating with open discovery and compact executive publication

### Decision

The production ETF prompt should no longer use a small fixed structural lane list as the front-end discovery gate.

### Chosen architecture

- open internal discovery across broad investable domains each run
- dynamic candidate-lane construction before publication
- persistent taxonomy as a back-end memory layer, not a front-end gate
- compact executive publication of only the best-ranked lanes
- continuity memory for retained lanes, new entrants, dropped lanes, and near-miss challengers

### Reason

This reduces omission risk while preserving premium executive selectivity.

---

## 2026-04-18 — Add starter pricing subsystem on main

### Decision

ETF has a starter explicit pricing subsystem rather than leaving pricing entirely as ad hoc retrieval inside the prompt.

### Chosen architecture

- `pricing/`
- `output/pricing/`
- pricing clients and audit writer
- pricing pass CLI

### Reason

This creates a machine-readable input/state layer for fresh ETF closes.

---

## 2026-04-21 — Make breadth assessment explicit through lane artifacts

### Decision

Broader discovery should be auditable through a matching machine-readable lane artifact and a compact visible omitted-lane block.

### Chosen architecture

- mandatory breadth assessment universe
- matching lane artifact in `output/lane_reviews/`
- compact omitted-lane proof in the published report
- helper validator in `validate_lane_breadth.py`

### Reason

Open discovery should not remain only a prompt intention.

---

## 2026-04-23 — Adopt English-canonical plus Dutch-companion bilingual delivery pattern

### Decision

ETF bilingual publication should use one canonical English pro report and one Dutch companion report derived from the completed English report.

### Chosen architecture

- English pro report remains canonical
- Dutch companion is a faithful language render
- one lane artifact remains tied to the English report
- paired filenames share date/version
- workflow can validate, render, and send both language versions

### Reason

This preserves analytical determinism while enabling bilingual delivery.

---

## 2026-04-27 — Introduce and enrich minimum explicit ETF state

### Decision

ETF should have explicit implementation state files instead of relying only on prior-report parsing and prompt continuity.

### Chosen architecture

- `tools/write_etf_minimum_state.py`
- `tools/write_etf_trade_ledger.py`
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `output/etf_trade_ledger.csv`
- dedicated state refresh workflow
- pre-send state derivation checks

### Reason

This moves ETF toward the FX-style state model while staying honest that ETF state is still report-derived.

---

## 2026-04-27 — Add lab-only ETF optimization layer

### Decision

ETF includes a lab-only optimization workbench using PyPortfolioOpt and yfinance-fetched history.

### Chosen architecture

- `tools/generate_pyportfolioopt_optimization_lab.py`
- `tools/fetch_etf_optimizer_prices_yfinance.py`
- `.github/workflows/lab-pyportfolioopt-optimization.yml`
- `lab_inputs/`
- `lab_outputs/`

### Reason

Optimization may be useful as QA/research, but must not become production authority without explicit review.

---

## 2026-05-05 — Add capital re-underwriting discipline and recommendation scorecard

### Decision

ETF now has an explicit capital re-underwriting discipline layer and a machine-readable recommendation scorecard.

### Chosen architecture

- `control/CAPITAL_REUNDERWRITING_RULES.md`
- `tools/write_etf_recommendation_scorecard.py`
- `output/etf_recommendation_scorecard.csv`
- pre-send scorecard derivation validation in `.github/workflows/send-weekly-report.yml`
- state-refresh support in `.github/workflows/refresh-etf-state-from-report.yml`

### Reason

The first-principles review identified a real process weakness: a holding can be described as replaceable, weakening, or difficult to reprice while still remaining unchanged for repeated runs.

The new discipline layer forces the model to ask whether each holding would be bought today with fresh cash, separates thesis validity from implementation quality, requires alternative duels for weak or replaceable holdings, flags factor overlap, tests hedge validity, classifies cash, and prevents indefinite `Hold but replaceable` inertia.

### Consequence

- Weak or replaceable holdings now need a named next action, alternative comparison, or explicit override.
- The next live ETF report should force clear review of SPY, PPA, PAVE, GLD, and cash policy.
- ETF state now includes portfolio state, valuation history, trade ledger, lane artifacts, pricing audits, and recommendation discipline memory.

---

## 2026-05-07 — Lock runtime-driven bilingual production baseline

### Decision

ETF now treats the runtime-driven pipeline as the stable production baseline.

### Chosen architecture

```text
pricing audit
→ lane discovery
→ runtime state
→ EN/NL report render
→ polish/linkify
→ validation
→ PDF/email delivery
```

### Reason

This path has produced received bilingual reports and resolves the prior architecture problem where markdown reports acted as hidden state, pricing source, continuity memory, and delivery artifact all at once.

### Consequence

- Markdown reports are presentation output, not primary state authority.
- Future changes should preserve the runtime flow and avoid manual markdown patching.
- Renderer changes should be limited to concrete output defects or validated improvements.
- The next discovery-maturity phase is historical relative-strength scoring.
- The next pricing-maturity phase is two-pass challenger pricing.

---

## 2026-05-07 — Validate historical relative-strength and two-pass challenger pricing baseline

### Decision

ETF now treats historical relative-strength scoring and two-pass challenger pricing as part of the validated production baseline.

### Chosen architecture

```text
pricing audit
→ historical relative strength
→ first-pass lane discovery
→ targeted challenger pricing
→ final lane discovery
→ runtime state
→ EN/NL report render
→ polish/linkify
→ validation
→ PDF/email delivery
```

### Reason

The workflow successfully passed after adding:

- `runtime/fetch_etf_relative_strength.py`
- historical 1m/3m return, trend, drawdown, volatility and relative-strength inputs
- `pricing/augment_challenger_pricing.py`
- targeted challenger pricing between first-pass and final discovery

### Consequence

- The Structural Opportunity Radar is now less dependent on configured priors.
- Top discovery challengers can receive targeted pricing before final scoring.
- Priced challengers are not automatically fundable; they only enable a fairer comparison.
- The next maturity steps are liquidity/tradability filtering, relative strength versus current holdings, and macro/fundamental freshness inputs.

---

## 2026-05-08 — Move strict branded sections to delivery HTML and validate rendered contract

### Decision

Sections with strict layout or clickable behavior are delivery-HTML responsibilities, not markdown-polish responsibilities.

### Chosen architecture

```text
runtime state
→ EN/NL markdown render
→ polish/linkify
→ delivery HTML overrides for strict sections
→ dynamic delivery HTML contract validator
→ PDF/email delivery
```

### Scope

This applies specifically to:

- Portfolio Action Snapshot
- Current Position Review

### Reason

Repeated markdown-level fixes could not reliably guarantee clickable ticker formatting or a stable Current Position Review table because the branded PDF renderer uses special panel logic. The stable solution is to render these strict sections directly from runtime state at the delivery HTML layer.

### Consequence

- `runtime/delivery_html_overrides.py` owns the final HTML for strict branded sections.
- `send_report_runtime_html.py` is the workflow delivery entrypoint.
- `tools/validate_etf_delivery_html_contract.py` dynamically reads holdings from runtime state and validates rendered delivery HTML before email send.
- The validator checks for real TradingView anchors, prevents raw markdown links, and ensures Current Position Review is a real HTML table.
- Future PDF layout defects in these sections should be fixed in the delivery HTML layer, not by more markdown post-processing.

---

## 2026-05-10 — Treat Dutch localization as a language-contract layer

### Decision

The Dutch ETF companion report is governed by a language-contract layer, not by ad-hoc markdown replacements or a separate research pass.

### Chosen architecture

```text
runtime state
→ English canonical report
→ Dutch companion render
→ Dutch localization contract pass
→ Dutch language quality validation
→ bilingual numeric parity validation
→ bilingual delivery HTML validation
→ PDF/email delivery
```

### Scope

This applies to:

- Dutch section titles
- Dutch table labels
- Dutch decision/status strings
- Dutch trigger phrases
- Dutch disclaimer wording
- allowed English financial terminology
- internal source labels that must never appear in client-facing Dutch text
- Dutch aliases used by validators and delivery checks

### Reason

The production debugging cycle showed that one-failure-at-a-time phrase fixes are fragile. The real issue was validator drift between:

- `runtime/nl_localization.py`
- `runtime/apply_nl_localization.py`
- `tools/validate_etf_dutch_language_quality.py`
- `send_report.py`
- `tools/validate_etf_delivery_html_contract.py`

Dutch output quality must be handled as an explicit contract across render, markdown validation, send-time parity validation, delivery HTML validation, and final email/PDF delivery.

### Consequence

- English remains the canonical analytical report.
- Dutch remains a derived companion, not an independent research pass.
- Dutch client-facing text should read as premium Dutch, not translated English with system artifacts.
- Validators must support both English canonical titles and Dutch companion titles.
- Numeric parity between English and Dutch must remain strict.
- Strict branded sections remain delivery HTML responsibilities.
- The next cleanup is to consolidate bilingual aliases so one Dutch label change does not require patches across several validators.

---

## 2026-05-11 — Render Section 7 equity curve from full valuation history

### Decision

Section 7 equity curve rendering must use the full machine-readable valuation history, not a hardcoded start/latest pair.

### Chosen architecture

```text
output/etf_valuation_history.csv
→ runtime/render_etf_report_from_state.py
→ Section 7 valuation table
→ embedded equity-curve chart
→ tools/validate_etf_equity_curve_history.py
→ ETF_EQUITY_CURVE_HISTORY_OK
```

### Scope

This applies to:

- Section 7 table rows
- embedded equity-curve chart
- latest NAV reconciliation with Section 15
- future regression protection before delivery

### Reason

A production report showed the equity curve with only two dots: the initial start date and the latest report date. The intermediate valuation dates existed in `output/etf_valuation_history.csv`, but the renderer ignored that file and hardcoded only start/latest. Because the chart generator uses Section 7 as its primary source, the chart also collapsed to two points.

### Consequence

- `runtime/render_etf_report_from_state.py` now reads `output/etf_valuation_history.csv` and adds or replaces the current runtime NAV for the report date.
- Section 7 now shows the full valuation history plus current NAV.
- The embedded chart now shows intermediate valuation dates.
- `tools/validate_etf_equity_curve_history.py` is wired into the send workflow.
- Fresh delivery fails before email if Section 7 has too few points, duplicate dates, or latest NAV does not reconcile with Section 15 total NAV.
