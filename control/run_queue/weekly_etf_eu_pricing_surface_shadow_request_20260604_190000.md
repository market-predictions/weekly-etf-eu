# Weekly ETF EU pricing surface shadow validation request

Requested: 2026-06-04 19:00 UTC

Purpose:

Run the non-production pricing-surface shadow validation workflow.

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
