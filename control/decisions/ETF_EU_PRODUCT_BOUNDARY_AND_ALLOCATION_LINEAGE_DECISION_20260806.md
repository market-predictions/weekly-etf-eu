# ETF EU product-boundary and allocation-lineage decision — 2026-08-06

## Decision

Weekly ETF EU is a separate product from Weekly FX. Active FX runners, scheduled FX generation, DailyTradeBias instructions and current FX output trees are prohibited in the Weekly ETF EU repository.

Portfolio release validity is established by protected-state lineage and explicit allocation authority, not by an invented universal position-weight or cash-floor percentage.

## Authority rules

```text
product=weekly_etf_eu
fx_generation_authority=false
allocation_method=protected_state_plus_explicit_authorized_mutation
valuation_only_preserves_tickers=true
valuation_only_preserves_shares=true
valuation_only_preserves_cash=true
share_or_cash_mutation_requires_explicit_decision=true
hard_maximum_position_weight_pct=null
mandatory_cash_floor_pct=null
```

## Weekly ETF donor interpretation

The donor requires a full weekly portfolio re-underwrite and does not define a universal 50% position cap or mandatory 35% cash reserve.

The donor's `75` value is a minimum pricing-coverage percentage. It is not portfolio concentration authority.

## Concentration treatment

- An allocator-created concentration that changes protected shares or cash without an explicit allocation decision is blocked.
- A market-driven concentration arising from unchanged protected shares and cash is disclosed and re-underwritten.
- A future hard concentration limit requires a separate, explicit and logged policy decision.

## Current protected state

```text
funded_tickers=VWCE,EUNA,SXR8,L0CK
position_count=4
cash_eur=50208.40
activation_id=ETF-EU-STAGE1-2026-08-04-20260804_STAGE1_30947965670_1
model_portfolio_only=true
real_broker_execution=false
```

## Consequence

The current remediation must pass:

1. repository product-boundary validation;
2. protected-state allocation-lineage validation;
3. completed-close funded pricing validation;
4. four-file bilingual report validation;
5. visual review;
6. independent pre-send assurance.

No transport or delivery claim follows from this decision alone.
