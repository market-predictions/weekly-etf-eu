# Weekly ETF EU — Product & Architecture Revision V2

**Status:** CANONICAL / ADOPTED FOR REALIZATION  
**Date:** 2026-08-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Evidence baseline:** live `main` observed at `d53c536efd4043c483d95b2f135d3a86e6d328b2`  
**Purpose:** replace accumulated implementation-first thinking with one customer-value-first product truth, one bounded modernization path, and an explicit technical/documentation debt retirement doctrine.
**Adoption:** approved for realization by principal instruction on 2026-08-30; GitHub main remains operational truth until governed integration.

> This document is the canonical product/architecture truth for the Revision V2 realization line. Live GitHub evidence remains operational truth for volatile branch/issue/claim state. This document deliberately does not mutate portfolio state, pricing, allocation, delivery, or broker behavior.

## Executive verdict

Weekly ETF EU does **not** need a rewrite. The project has valuable primitives: ISIN-first UCITS identity, exact trading-line binding, current-close pricing authority, protected portfolio state and ledger, current re-underwriting, donor discovery, independent assurance, deterministic artifact validation, guarded delivery, and receipt discipline.

The central problem is **semantic multiplicity**: too many files can look like current truth, too many runtime modules can look like a valid executor, too many output trees can look current, and too many post-render repair layers can change client semantics after canonical-looking state was built.

The product is therefore:

> **A weekly EU-investable capital-decision and accountability system that tells the client where the model portfolio stands, whether the process is adding value versus a deliberately simple investable comparator, which holdings still deserve capital, which alternatives are better, what should change this week, and why — then communicates that conclusion consistently in a premium client report.**

The report is the interface. Governance is the safety system. Code is the mechanism. **The product is the investment decision plus accountable evidence.**

The target is a **Thin Current Kernel**:

1. persistent authoritative domain state;
2. fresh current market/investment evidence;
3. one per-run canonical `review_state`;
4. pure NL/EN projections from that state;
5. frozen delivery artifacts;
6. independent assurance and receipt evidence around the boundary.

**Simplification is not a later phase. Debt retirement is part of Definition of Done for every feature.**

---

# 1. First-principles product truth

## 1.1 Customer job to be done

A Weekly ETF EU client should be able to answer:

1. **Where do I stand?** Current NAV, cash, positions, P/L, risk and relevant changes.
2. **Is the process working?** Portfolio result versus a simple investable comparator, with transparent cash drag and major contributors/detractors.
3. **Does every funded position still deserve capital today?** After fresh re-underwriting, not because it was bought before.
4. **Is there a materially better alternative?** Broad discovery first, then EU/UCITS investability and implementation gates.
5. **What changes this week?** Add, hold, reduce, replace, close or deliberately keep cash — with rationale, confidence, invalidation trigger and next review condition.

Everything else is supporting evidence, implementation detail, governance or archive.

## 1.2 What the product is not

Weekly ETF EU is not primarily a PDF generator, bilingual formatting system, pricing-provider consensus machine, workflow-governance showcase, donor-parity exercise, maximum-ticker-count optimizer, collection of validators, or historical artifact museum.

## 1.3 Core product invariant

A feature is valuable only if it improves at least one of: investment decision quality; truth/freshness of evidence; explainability/accountability; client comprehension; deterministic reliability; safe delivery; maintainability that protects the above.

---

# 2. Design decisions

The ten adversarial review passes behind this revision produced these stable conclusions:

1. **Report is interface, not product.** Optimize around decisions and accountability, not factory mechanics.
2. **No big-bang cleanup.** First do bounded Truth & Execution Convergence; thereafter retire debt feature-by-feature.
3. **Accountability enters through canonical state.** Do not bolt benchmark metrics onto the patch stack.
4. **No mega-state.** Keep protected persistent domain truth separate from immutable per-run `review_state`.
5. **Retired executors leave current namespaces.** Forensic artifacts may remain only in explicit archive paths.
6. **Disabled workflows are not sufficient containment.** Current production code needs an obvious current package/entrypoint boundary.
7. **Donor parity is not destination.** Reuse proven primitives/behavior, never donor state/topology by default.
8. **Validators fail, not repair.** Semantic corrections belong upstream in state building or pure rendering.
9. **LIVE_FIRST / NARRATIVE_LIGHT.** Stable docs describe authority/policy; live repo/PR/issue/output evidence describes volatile reality.
10. **Debt retirement is Definition of Done.** Superseded docs, executors, aliases, fixtures and output routes leave current authority surfaces.

---

# 3. Canonical product truth

## 3.1 Product mission

Weekly ETF EU exists to make and communicate a disciplined weekly model-portfolio capital decision for a European investor using investable EU/UCITS instruments and to measure whether that process is adding value versus a deliberately simple, stable, investable comparator.

## 3.2 Decision sequence

```text
current protected holdings + cash + ledger
                ↓
fresh identity-bound market evidence
                ↓
current investment evidence + broad challengers
                ↓
re-underwrite every funded holding
                ↓
rank investment attractiveness / portfolio fit
                ↓
apply EU/UCITS fundability and implementation gates
                ↓
explicit model allocation decision
                ↓
measure result versus stable comparator(s)
                ↓
one canonical review state
                ↓
client report + delivery
```

Fundability and pricing determine whether an idea can be implemented and valued. They are not themselves evidence that it is the best investment.

## 3.3 Evidence authority principles

- Current protected portfolio state and trade ledger outrank narrative memory.
- Current exact-date pricing evidence outranks prior report prices.
- Current re-underwriting outranks historical `last_action` or old target metadata.
- Donor discovery is opportunity evidence, not EU funding authority.
- A correct exact-date primary close can be valuation-grade without a current verifier when identity binding is correct; a verifier improves confidence; disagreement fails closed.
- Benchmark/accountability is evidence about process quality; it does not mechanically authorize trades.
- Client text never creates portfolio mutation authority.

## 3.4 Benchmark/accountability contract

Use one primary investable comparator aligned with the intended risk posture and optionally one broad global-equity UCITS contextual reference. Do not change comparators opportunistically. Record identity, methodology and effective date; compare on compatible valuation dates; surface missing benchmark data explicitly.

Minimum accountability surface:
- portfolio return: period and since inception;
- comparator return: same periods;
- active return in percentage points;
- portfolio drawdown vs comparator drawdown;
- cash drag/contribution where measurable;
- top contributor and top detractor;
- position-level contribution;
- material transaction/turnover note;
- costs only where evidenced.

No Sharpe/Sortino/Brinson/optimizer layer is required for the first release.

---

# 4. Target architecture — Thin Current Kernel

## 4.1 Four layers plus governance boundary

### Layer 1 — Decision framework
Defines fresh-cash test, thesis/implementation quality, contribution/drag, overlap/concentration, replacement duel, cash deployment rationale, current action and invalidation trigger.

### Layer 2 — Input/state contract
Persistent authoritative inputs:
- `portfolio_state` — funded holdings, shares, cash and stable identity;
- `trade_ledger` — authoritative model mutations;
- `valuation_accountability_history` — dated portfolio/comparator observations;
- `recommendation_memory` — re-underwriting/action-clock continuity;
- UCITS symbol/trading-line registry;
- current pricing evidence;
- donor discovery/proxy evidence with explicit non-authority.

### Layer 3 — Per-run review contract
One immutable/frozen `review_state_<run_id>.json` contains all client-semantic facts:
- report/completed-close date;
- current valuation and funded positions;
- current action per position;
- re-underwriting evidence/confidence;
- challenger ranking and implementation gates;
- allocation decision/no-change rationale;
- benchmark/accountability metrics;
- material macro context;
- provenance/confidence/unresolved fields.

After freeze, no downstream component may recalculate NAV, choose a different authoritative price, change an investment action, change allocation semantics, or rewrite benchmark performance.

### Layer 4 — Output/delivery contract
Pure projections only:

```text
review_state
  ├── NL HTML
  ├── EN HTML
  ├── NL text/Markdown
  └── EN text/Markdown

NL/EN HTML -> PDF
approved HTML + approved text + approved PDF -> guarded email
```

PDF derives from exact approved HTML. Email consumes exact approved artifacts and does not re-render investment content.

### Governance boundary
Independent assurance and guarded delivery validate/protect the exact frozen candidate; they do not create investment logic.

## 4.2 Target-path exclusions
The current path must not require semantic post-render reconciliation, report-to-state reverse derivation, parallel renderers for the same product, multiple live senders, live-looking historical target weights, volatile operational truth duplicated in narrative files, donor runtime execution in EU production, disabled workflows sitting indefinitely beside active workflows, or compatibility aliases without sunset.

---

# 5. Debt retirement doctrine

Observed high-risk debt categories and required treatment:

| Debt | Required treatment |
|---|---|
| Stale read-first control files | Stable authority/policy only; volatile state must be resolved live |
| US `docs/ETF_MINIMUM_STATE_MODEL.md` | Replace with EU persistent-state + per-run review-state contract |
| Historical roadmaps in current namespace | One current roadmap pointer; history under explicit archive |
| Generic/US bootstrap/prompt lineage | EU-specific stable bootstrap; historical prompts non-authoritative |
| Callable historical runtime families | Reachability classification; current/supporting vs archive/delete |
| `finalize/reconcile/polish/scrub/synchronize/fix` semantic patch stack | Move semantics upstream and retire patch responsibility as covered |
| Misleading `consensus` pricing naming | Accurate current naming + bounded deprecated alias |
| Historical target weights in live-looking state | Namespace as historical metadata or move to ledger/history |
| `.yml.disabled` in workflows | Archive forensic subset outside workflow namespace; delete rest |
| Multiple senders/renderers | One current entrypoint per responsibility after proof |
| Output namespace sprawl | Stop new writes to legacy roots; converge to state/current/evidence/history |
| Stale open PR/issue lines | Live-check then close as superseded with successor pointer |

No file is deleted solely because its name looks old. Retirement requires reachability/reference evidence or explicit historical disposition.

---

# 6. Donor architecture policy

Before porting donor code, answer:
1. Is the underlying problem identical?
2. Is the donor solution still the simplest proven solution?
3. Can it be reused without importing donor state/authority?
4. Which EU-specific gates wrap it?
5. Which existing EU implementation becomes removable?

If #5 has no answer, the port is probably creating a parallel path.

Proven donor behavior may be reused for discovery, re-underwriting, recommendation/action-clock memory, challenge/replacement logic, deterministic state, equity-curve parity and generic rendering/delivery primitives. Never import donor portfolio state, report filenames, pricing outputs, workflows, US investability assumptions, recipients or historical patch topology as EU authority.

---

# 7. Realization roadmap

## R0 — Truth & Execution Convergence
Bounded no-investment-behavior-change slice:
- stable read-first truth;
- executor reachability inventory/quarantine;
- workflow archive cleanup;
- compatibility naming/state hygiene;
- stale development-line cleanup.

**Exit:** a new worker can identify product truth, candidate executor and sender without archaeology.

## R1 — Accountable Decision Kernel
Build stable comparator contract, accountability history, one canonical per-run review state and minimum accountability rendering. Retire duplicate downstream calculations.

**Exit:** one dated review state answers “did the portfolio add value, why, and what deserves capital now?” without prior report prose.

## R2 — Decision-First Client Surface
First page: NAV/cash/invested, weekly action, comparator/active return, contributors/detractors, cash rationale, best challenger, biggest risk, confidence/unresolved. Funded-position table: action, value/weight, fresh-cash view, rationale, contribution, best alternative, invalidation/trigger, confidence. Factory detail moves to appendix.

**Exit:** client understands decision/accountability from first 1–2 pages.

## R3 — Pure Render Convergence
NL/EN Markdown/HTML derive from same review state; PDF from exact HTML; validators fail-only; retire redundant semantic patch/render/send paths; converge output namespace.

**Exit:** one investment fact changes in one state-building path.

## R4 — Evidence & Epistemic Quality
Add claim provenance, confidence, unresolved evidence, freshness/expiry and source-quality distinctions within the same evidence/review-state plane.

**Exit:** material client claims are traceable without a parallel authority system.

---

# 8. Mandatory Definition of Done

A feature is not DONE until all applicable conditions hold:

### Authority
- one explicit current authority location;
- no superseded read-first contradiction;
- history archived/non-authoritative;
- no unnecessary duplicated live state in narrative docs.

### Execution
- one current executor path uses the behavior;
- old paths deleted/archived outside current namespace;
- no parallel sender/renderer/state writer can produce the same current product without explicit authority.

### State
- behavior lives at the correct persistent/per-run layer;
- renderers do not recompute authoritative facts;
- historical fields cannot masquerade as current authority.

### Output
- NL/EN/HTML/Markdown/PDF agree on material facts;
- PDF derives from exact approved HTML;
- delivery sends frozen artifacts only.

### Compatibility
- alias has owner and explicit sunset;
- active callers migrate before removal;
- misleading legacy terminology does not remain indefinitely.

### Tests
- positive tests prove intended behavior;
- negative tests prove retired behavior cannot reappear;
- fixtures do not preserve stale semantics just to remain green.

### Documentation
- `SYSTEM_INDEX` reflects stable architecture;
- current roadmap reflects capability;
- superseded docs are removed/archived in same change or bound follow-up;
- stale PR/issue lines are not left looking current.

---

# 9. Deliberate non-goals

Do not build: a database to synchronize narrative state; event bus; separate orchestration service; generic provider plugin framework; second state plane; universal report AST when typed JSON/Python suffices; custom templating engine without need; production optimizer before accountability; ornamental institutional risk metrics; automated benchmark switching; multiple active preview/production render paths; or a background process whose only job is keeping `CURRENT_STATE.md` fresh.

---

# 10. Success criteria

## Product
- First page answers what changed, why, whether process adds value and what to do next.
- Every funded holding has a fresh-cash decision and best alternative.
- Cash is explained deliberately.
- Stable comparator makes value added/destroyed visible.

## Architecture
- One persistent portfolio state.
- One trade ledger.
- One recommendation/re-underwriting memory.
- One per-run review state.
- One current client rendering path.
- One current delivery entrypoint.
- Historical executors are outside current executable/read-first namespaces.

## Reliability
- Exact-date pricing authority preserves primary + optional verification semantics.
- NL/EN/HTML/Markdown/PDF material facts cannot diverge without a failing gate.
- No client semantics change after review-state freeze.
- No delivery success without real evidence.

## Maintainability
- Current truth is findable in minutes.
- Features replace/remove code rather than stack patches.
- Active render/send/state paths trend down.
- Completed work retires stale docs/executors.

---

# 11. Stable decision record

| ID | Decision | Rationale |
|---|---|---|
| EU-REV2-01 | Product = weekly capital decision + accountability; report = interface | Align engineering with customer value |
| EU-REV2-02 | Debt retirement is Definition of Done | Prevent patch-stack growth |
| EU-REV2-03 | Persistent domain state + one per-run review state | Avoid report-derived truth and mega-state |
| EU-REV2-04 | Client semantics freeze at review state | Eliminate surface-specific semantic drift |
| EU-REV2-05 | Validators fail; do not repair content | Push correctness upstream |
| EU-REV2-06 | Donor reuse = primitive/behavior reuse, not topology parity | Capture value without donor debt |
| EU-REV2-07 | Retired executors leave current namespaces | Prevent accidental resurrection |
| EU-REV2-08 | Operational truth is live-first; narrative is stable/light | Remove stale dual writes |
| EU-REV2-09 | Benchmark-relative accountability is top-level product requirement | Make investment value measurable |
| EU-REV2-10 | Compatibility aliases require explicit sunset | Prevent legacy semantics becoming permanent |

---

# 12. Adoption and realization authority

This architecture is implemented under `docs/runbooks/WEEKLY_ETF_EU_REALIZATION_RUNBOOK_V1.md` and canonical `market-predictions/control-plane` governance. It does not itself create report-delivery, portfolio-mutation, broker, pricing-source promotion, merge or independent-assurance authority.
