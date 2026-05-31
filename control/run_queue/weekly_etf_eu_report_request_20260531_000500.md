# Weekly ETF EU bootstrap output validation request

requested_at_utc: 2026-05-31T00:05:00Z
requested_run_date: 2026-05-31
mode: eu_ucits_output_contract_validation
production_delivery: false

## Request
Run the EU/UCITS bootstrap validation workflow after fixing markdown normalization in the EU output contract validator.

## Expected behavior
- Validate EU control files and config stubs.
- Validate cash-only EU state.
- Validate no U.S.-listed ETF appears as an EU holding.
- Render non-delivery EU markdown report skeletons:
  - output/weekly_etf_eu_review_YYMMDD.md
  - output/weekly_etf_eu_review_nl_YYMMDD.md
- Validate EU output contract with markdown-emphasis normalization.
- Confirm inherited U.S. production sender remains disabled.
- Commit generated EU markdown report skeletons back to output/.
- Do not run pricing.
- Do not mutate portfolio state.
- Do not generate PDFs.
- Do not send email.
