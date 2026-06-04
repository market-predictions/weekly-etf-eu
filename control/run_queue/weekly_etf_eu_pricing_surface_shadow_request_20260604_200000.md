# Weekly ETF EU pricing surface shadow validation request

Requested: 2026-06-04 20:00 UTC

Purpose:

Re-run the non-production pricing-surface shadow validation workflow after refining the pricing-surface validator to allow safe negated funding disclaimers while still blocking positive authority/funding claims.

Expected workflow:

```text
.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml
```

Authority boundaries:

```text
funding_authority=false
portfolio_mutation=false
production_delivery=false
no PDF generation
no email delivery
no delivery receipt
no candidate promotion to fundable
```
