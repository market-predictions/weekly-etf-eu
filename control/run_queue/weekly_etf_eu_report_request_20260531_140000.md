# Weekly ETF EU candidate-report validation request

requested_at_utc: 2026-05-31T14:00:00Z
requested_run_date: 2026-05-31
mode: eu_ucits_candidate_report_validation
production_delivery: false
portfolio_mutation: false
funding_authority: false

## Request
Run the EU/UCITS bootstrap validation workflow after extending the Dutch-first report with the UCITS candidate registry and pricing-preflight status.

## Expected behavior
- Validate EU control files and config stubs.
- Validate UCITS symbol registry and investability contract.
- Build and validate UCITS pricing candidates.
- Run and validate non-authoritative UCITS pricing preflight.
- Validate cash-only EU state.
- Render Dutch-first and English companion candidate report skeletons.
- Validate EU output contract.
- Validate EU candidate-report contract.
- Confirm inherited U.S. production sender remains disabled.
- Commit markdown and pricing-preflight artifacts.
- Do not mutate portfolio state.
- Do not mark any candidate fundable.
- Do not generate production PDFs.
- Do not send email.
