# Weekly ETF EU UCITS pricing-line preflight request

requested_at_utc: 2026-05-31T13:15:00Z
requested_run_date: 2026-05-31
mode: eu_ucits_pricing_line_preflight
production_delivery: false
portfolio_mutation: false
funding_authority: false

## Request
Run the EU/UCITS bootstrap validation workflow after adding the UCITS pricing-line contract, pricing candidate extractor, candidate validator, non-authoritative pricing preflight and preflight validator.

## Expected behavior
- Validate EU control files and config stubs.
- Validate UCITS symbol registry.
- Validate UCITS investability contract.
- Build UCITS pricing candidate artifact from verified-but-not-funded registry entries.
- Validate UCITS pricing candidate artifact.
- Run non-authoritative UCITS pricing preflight.
- Validate UCITS pricing preflight artifact.
- Validate cash-only EU state.
- Validate no U.S.-listed ETF appears as an EU holding.
- Render non-delivery EU markdown report skeletons.
- Validate EU output contract.
- Confirm inherited U.S. production sender remains disabled.
- Commit markdown and pricing-preflight artifacts.
- Do not mutate portfolio state.
- Do not mark any candidate fundable.
- Do not generate production PDFs.
- Do not send email.
