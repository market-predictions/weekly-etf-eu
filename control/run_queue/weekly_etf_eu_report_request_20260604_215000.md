# Weekly ETF EU bootstrap validation request

Requested: 2026-06-04 21:50 UTC

Purpose:
Run the main EU bootstrap validation workflow after promoting it to the agreement-aware valuation and pricing-surface wrapper path.

Expected workflow:
.github/workflows/send-weekly-etf-eu-report.yml

Authority boundaries:
- funding_authority=false
- portfolio_mutation=false
- production_delivery=false
- no PDF generation
- no email delivery
- no delivery receipt
- no candidate promotion to fundable
