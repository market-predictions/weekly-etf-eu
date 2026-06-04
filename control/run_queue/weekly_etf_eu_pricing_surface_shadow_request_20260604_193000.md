# Weekly ETF EU pricing surface shadow validation request

Requested: 2026-06-04 19:30 UTC

Purpose:

Re-run the non-production pricing-surface shadow validation workflow after fixing the agreement-aware wrapper to use a conservative shadow policy copy compatible with the current temporary Yahoo policy.

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
