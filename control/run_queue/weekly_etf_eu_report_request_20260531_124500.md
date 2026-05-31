# Weekly ETF EU UCITS registry validation request

requested_at_utc: 2026-05-31T12:45:00Z
requested_run_date: 2026-05-31
mode: eu_ucits_registry_validation
production_delivery: false

## Request
Run the EU/UCITS bootstrap validation workflow after fixing YAML syntax in the UCITS symbol registry.

## Expected behavior
- Parse config/ucits_symbol_registry.yml successfully.
- Validate UCITS symbol registry.
- Validate UCITS investability contract.
- Validate cash-only EU state.
- Validate no U.S.-listed ETF appears as an EU holding.
- Render non-delivery EU markdown report skeletons.
- Validate EU output contract.
- Confirm inherited U.S. production sender remains disabled.
- Do not run pricing.
- Do not mutate portfolio state.
- Do not generate PDFs.
- Do not send email.
