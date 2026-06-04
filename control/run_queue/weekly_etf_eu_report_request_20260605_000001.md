# Weekly ETF EU Dutch-first production surface validation request

Requested: 2026-06-05 00:00 UTC

Purpose:

Run the main EU bootstrap validation workflow after WP5 final report-surface integration.

Expected workflow:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

Expected validation focus:

```text
runtime.render_etf_eu_report_with_pricing_surface
runtime.etf_eu_fundability_surface
tools/validate_etf_eu_output_contract.py --require-production-dutch-first
tools/validate_etf_eu_pricing_surface.py --require-production-dutch-first
tools/validate_etf_eu_fundability_surface.py
tools/validate_ucits_fundability_promotion_contract.py --artifact output/fundability/ucits_fundability_gate_<run_id>.json
```

Authority boundaries:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
no PDF generation
no email delivery
no delivery receipt
```
