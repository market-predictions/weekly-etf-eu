# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-06-04 — Reconcile Yahoo UCITS pricing policy authority boundary

### Decision

Yahoo/yfinance may remain in UCITS source policy as temporary connectivity/display evidence, but it is not agreement-gate valuation-grade authority.

### Chosen architecture

- `config/ucits_pricing_source_policy.yml` keeps Yahoo symbols only as `non_authoritative_connectivity_only` evidence.
- Yahoo rows must set `valuation_grade_eligible=false`, `accept_as_valuation_grade=false`, and `counts_for_market_close_agreement=false`.
- `control/DATA_SOURCE_METADATA.md` remains the source-role register for source-category behavior.
- The agreement gate may preserve Yahoo evidence for diagnostics/display, but cannot count Yahoo toward `min_independent_sources` or populate valuation authority fields.

### Reason

Previous policy wording described a temporary Yahoo verified fallback and marked Yahoo as valuation-grade eligible. That conflicted with source metadata and the agreement gate, which treat Yahoo as connectivity/provisional evidence only.

### Consequence

- Yahoo can support symbol reachability and display continuity.
- Yahoo cannot create `valuation_grade=true`.
- Yahoo cannot satisfy agreement-gate market-close agreement by itself or as a counted source.
- Future promotion requires a new explicit decision log entry plus validator-backed implementation.
- No funding authority, portfolio mutation, report delivery, PDF generation, or email behavior changes.

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
