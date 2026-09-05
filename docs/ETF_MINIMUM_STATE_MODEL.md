# Weekly ETF EU — Minimum State Model

**Status:** CURRENT STATE CONTRACT  
**Architecture:** `docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md`

## Purpose

Weekly ETF EU separates **persistent domain truth** from **per-run client-semantic truth**. Reports are projections of state; they are never allowed to recreate portfolio authority by parsing prior prose.

This replaces the historical U.S. `weekly-etf` report-derived state description that previously lived at this path.

## 1. Persistent domain truth

Persistent state survives across review runs and is authoritative only for its defined concern.

### `output/etf_eu_portfolio_state.json`
Protected current portfolio facts:
- stable instrument identity;
- funded share counts;
- cash;
- current normalized holdings state;
- stable portfolio metadata needed for valuation continuity.

It must not expose historical activation/transition target weights as if they were current allocation authority.

### `output/etf_eu_trade_ledger.csv`
Authoritative model mutation history. A report row or target proposal cannot substitute for ledger authority.

### `output/etf_eu_valuation_history.csv`
Current dated portfolio valuation history. Under Architecture V2 this is extended/converged toward valuation/accountability history including the stable comparator on compatible dates. Historical portfolio observations remain append-only evidence; current valuation must come from current completed-close evidence.

### `output/etf_eu_recommendation_scorecard.csv`
Recommendation/re-underwriting continuity and action-clock memory. Historical actions do not automatically authorize a current Hold/Add/Reduce decision; each funded holding is re-underwritten from fresh evidence.

### `config/ucits_symbol_registry.yml`
Stable ISIN-first/trading-line identity and investability mapping. It is identity authority, not funded-state authority.

## 2. Fresh evidence inputs

A review run combines persistent domain truth with fresh evidence such as:
- exact completed-session pricing evidence bound to canonical UCITS trading lines;
- current re-underwriting evidence;
- broad donor discovery/challenger evidence with explicit non-authority;
- EU-local UCITS fundability and implementation evidence;
- comparator pricing evidence on compatible valuation dates;
- material macro evidence where it changes interpretation.

Current pricing authority is defined by `control/PRICING_AUTHORITY_CURRENT.md`: a qualified correctly bound exact-date primary close may be valuation-grade without a current verifier; an available exact verifier upgrades confidence; accepted same-date disagreement fails closed.

## 3. Per-run review truth

Each production candidate creates exactly one immutable semantic object:

`review_state_<run_id>.json`

Minimum contract:

```json
{
  "schema_version": "etf_eu_review_state_v1",
  "run_id": "...",
  "report_date": "YYYY-MM-DD",
  "completed_close_date": "YYYY-MM-DD",
  "portfolio": {
    "base_currency": "EUR",
    "invested_value_eur": 0.0,
    "cash_eur": 0.0,
    "nav_eur": 0.0,
    "positions": []
  },
  "accountability": {
    "primary_comparator": {},
    "portfolio_return_pct": null,
    "comparator_return_pct": null,
    "active_return_pp": null,
    "portfolio_drawdown_pct": null,
    "comparator_drawdown_pct": null,
    "cash_contribution": null,
    "position_contributions": [],
    "top_contributor": null,
    "top_detractor": null
  },
  "decisions": [],
  "challengers": [],
  "evidence": {
    "pricing": {},
    "claims": [],
    "unresolved": []
  },
  "freeze": {
    "semantic_frozen": true,
    "state_digest_sha256": "..."
  }
}
```

Exact field growth is allowed when it improves product truth without creating another state plane. The state must remain deterministic for fixed inputs.

## 4. Freeze invariant

After `review_state` freeze, downstream components may format/localize/style but may not:
- recalculate NAV to a different value;
- select a different authoritative price;
- change an investment action or allocation rationale;
- change benchmark/comparator performance;
- infer missing portfolio authority from report prose;
- silently repair contradictory semantic facts.

A semantic change requires rebuilding a new review state, producing a new candidate head and obtaining fresh exact-head assurance where required.

## 5. Output projections

All client formats consume the same review state:

```text
review_state
  ├── NL Markdown/text
  ├── EN Markdown/text
  ├── NL HTML -> NL PDF
  └── EN HTML -> EN PDF
```

Material numeric and decision facts must reconcile across languages and formats. PDF derives from the exact approved HTML. Guarded email sends exact approved artifacts and does not re-render investment content.

## 6. Authority order

```text
explicit current allocation decision
> protected portfolio state + trade ledger
> current exact-date pricing + current re-underwriting/accountability evidence
> current donor opportunity evidence mapped through EU/UCITS gates
> historical reports, targets, work packages and strategy context
```

Client text and historical report sections are never a write-authority source for protected state.

## 7. State update responsibilities

- Portfolio/share/cash and ledger mutation remains separately governed and explicit.
- Valuation/accountability history is written only from reconciled current evidence.
- Recommendation memory records current re-underwriting outcomes without turning historical actions into current authority.
- `review_state` is per-run and immutable after freeze.
- Renderers are projections, not state builders or repair engines.

## 8. Non-goals

Do not add a database, second state service, report AST, synchronization daemon or event bus solely to implement this contract. Repository JSON/CSV state plus deterministic Python builders/renderers are sufficient until a demonstrated problem proves otherwise.
