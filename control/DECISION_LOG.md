# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-06-05 — WP9 blocked delivery manifest operational integration decision

### Decision

WP9 operationalizes a blocked delivery manifest in the main workflow.

The delivery manifest is evidence/control metadata only. It does not enable production delivery, PDF generation, email delivery, delivery receipts, portfolio mutation, funding authority, valuation authority, or candidate promotion.

Delivery remains blocked until a later explicit delivery implementation creates and validates a real receipt path.

### Chosen architecture

```text
main EU bootstrap workflow
→ runtime.build_etf_eu_delivery_manifest
→ output/delivery/etf_eu_delivery_manifest_<run_id>.json
→ tools/validate_etf_eu_delivery_manifest.py
→ artifact commit as evidence
```

The verified WP9 artifact is:

```text
output/delivery/etf_eu_delivery_manifest_20260605_074604.json
```

### Stable authority rules

```text
status=blocked_design_only
delivery_enabled=false
receipt_status=not_created
funding_authority=false
portfolio_mutation=false
valuation_grade_promotion=false
candidate_promotion_to_fundable=false
pdf_generation=false
email_delivery=false
delivery_receipt=false
production_delivery=false
```

### Reason

The report workflow needs a deterministic delivery-control artifact before any future send layer can be considered. A manifest can prove that all current delivery gates remain blocked without becoming delivery itself.

### Consequence

WP9 is completed as blocked delivery manifest operational integration. The main workflow can produce and commit a delivery manifest as evidence, but real delivery remains unavailable until a separate receipt path, recipient policy, secrets policy, and explicit delivery authorization exist.

---

## 2026-06-05 — WP12 email delivery dry-run authority decision

### Decision

WP12 email delivery dry-run is a metadata/control package only.

It may describe future delivery packaging, subject/body previews, attachment paths, delivery-manifest references, and shadow-PDF references, but it does not authorize or perform sending.

No SMTP, external mail API, recipient activation, delivery receipt, PDF generation, production delivery, portfolio mutation, funding authority, valuation authority, or candidate promotion is enabled.

### Chosen architecture

```text
control/ETF_EU_EMAIL_DRY_RUN_CONTRACT_V1.md
→ runtime/build_etf_eu_email_dry_run.py
→ output/delivery/email_dry_run_<run_id>.json
→ tools/validate_etf_eu_email_dry_run.py
```

The verified WP12 sample artifact is:

```text
output/delivery/email_dry_run_20260605_000000.json
```

### Stable authority rules

```text
status=design_only_blocked
send_attempted=false
email_delivery=false
delivery_receipt=false
production_delivery=false
mail_transport_configured=false
external_mail_api_enabled=false
send_function_present=false
recipient_activation=false
pdf_generation=false
```

### Reason

The future delivery layer needs a deterministic preview/control package before any real sending can be considered. A dry-run artifact can describe what would be packaged later while proving that no send attempt, recipient activation, mail transport, PDF generation, delivery receipt, or production delivery exists.

### Consequence

WP12 is completed as an email delivery dry-run contract only. It is not workflow-integrated real delivery. WP13 real delivery remains blocked until WP9, WP10, WP11 and WP12 are verified and recipient allowlist, SMTP/secrets policy and delivery receipt validator exist.

---

## 2026-06-05 — WP11 shadow PDF rendering design/test authority decision

### Decision

WP11 shadow PDF rendering is allowed only as a local/shadow artifact path.

PDF generation remains:

```text
pdf_generation=shadow_only
```

No production delivery, email delivery, delivery receipt, or workflow integration is authorized.

Workflow integration must wait until WP9 delivery manifest operational integration is complete and a later explicit decision authorizes it.

### Chosen architecture

```text
Dutch Markdown report + English Markdown report
→ runtime/render_etf_eu_shadow_pdf.py
→ output/pdf/weekly_etf_eu_review_nl_<date>.pdf
→ output/pdf/weekly_etf_eu_review_<date>.pdf
→ output/pdf/etf_eu_shadow_pdf_manifest_<run_id>.json
→ tools/validate_etf_eu_shadow_pdf.py
```

### Stable authority rules

```text
production_delivery=false
email_delivery=false
delivery_receipt=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
candidate_promotion=false
workflow_integrated=false
```

### Reason

PDF rendering can be prepared as an artifact-format capability without converting it into client delivery. A rendered PDF is not a delivery receipt and must not be used to claim production delivery.

### Consequence

WP11 is completed as a shadow PDF design/test path only. It is not workflow-integrated, not production delivery, not email delivery, and not a delivery receipt.

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
