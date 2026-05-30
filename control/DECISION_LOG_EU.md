# Weekly ETF EU Review OS — Decision Log

## 2026-05-30 — Split EU/UCITS model from U.S.-ETF baseline

### Decision

Create and maintain `market-predictions/weekly-etf-eu` as a separate European / Dutch-client UCITS ETF review system.

### Authority

- `market-predictions/weekly-etf` remains the U.S.-ETF model baseline.
- `market-predictions/weekly-etf-eu` becomes the UCITS ETF model for Dutch/EU clients.

### Rationale

This is not a translation problem. The EU model changes the investable universe, state contract, instrument identity, pricing identifiers, output language and validation rules.

### Stable rules

- U.S.-listed ETFs are research proxies only in the EU repo.
- UCITS ETFs are the investable instruments.
- ISIN-first identity is required for funded EU holdings.
- Production delivery remains blocked until EU validators pass.

---

## 2026-05-30 — Disable inherited U.S. production workflow in EU repo

### Decision

Disable the inherited `.github/workflows/send-weekly-report.yml` production send path in `weekly-etf-eu`.

### Rationale

The mirror clone copied the full U.S.-ETF pricing, model execution, PDF and email workflow. Running that in the EU repo before migration would risk sending a U.S.-ETF report from the EU environment.

### Result

The inherited workflow now emits only a disabled-workflow message and performs no pricing, portfolio mutation, PDF rendering or email delivery.

---

## 2026-05-30 — Bootstrap validation is non-delivery only

### Decision

The first EU workflow is `Weekly ETF EU UCITS bootstrap validation`, and it is validation-only.

### Validated

- EU control files exist.
- EU config stubs exist.
- EU cash-only state exists.
- No U.S. ETF appears as an EU holding.
- Inherited U.S. production sender is disabled.
- No delivery is attempted.

### Rationale

The EU repo should become operational only after UCITS registry, pricing, output and delivery contracts are explicit.
