# Weekly ETF EU bootstrap validation request

requested_at_utc: 2026-05-30T21:00:00Z
requested_run_date: 2026-05-30
mode: eu_ucits_bootstrap_validation
production_delivery: false

## Request
Run the EU/UCITS bootstrap validation workflow.

## Expected behavior
- Validate EU control files exist.
- Validate EU config stubs exist.
- Validate cash-only EU state.
- Validate no U.S.-listed ETF appears as an EU holding.
- Validate inherited U.S. production send workflow is disabled.
- Do not run pricing.
- Do not mutate portfolio state.
- Do not generate PDFs.
- Do not send email.
