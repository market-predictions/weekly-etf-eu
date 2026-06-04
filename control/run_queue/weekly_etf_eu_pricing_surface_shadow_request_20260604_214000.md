# Weekly ETF EU pricing surface shadow validation request

Requested: 2026-06-04 21:40 UTC

Purpose:
Re-run the non-production pricing-surface shadow validation workflow on latest main after validator stabilisation and control-file consolidation.

Expected workflow:
.github/workflows/weekly-etf-eu-pricing-surface-shadow.yml

Authority boundaries:
- funding_authority=false
- portfolio_mutation=false
- production_delivery=false
- no PDF generation
- no email delivery
- no delivery receipt
- no candidate promotion to fundable
