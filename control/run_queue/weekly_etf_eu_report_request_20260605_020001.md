# Weekly ETF EU Dutch-first production surface validation request

Requested: 2026-06-05 02:00 UTC

Purpose:

Re-run the main EU bootstrap validation workflow after the WP5 strict-output validator fix.

Root cause of previous failure:

```text
Strict Dutch-first validation scanned historical weekly_etf_eu_review*.md files in output/.
Older reports predated the WP5 production maturity layer.
```

Patch applied:

```text
tools/validate_etf_eu_output_contract.py now supports --report-suffix.
.github/workflows/send-weekly-etf-eu-report.yml now validates only the current report pair with $ETF_EU_REPORT_SUFFIX.
```

Expected workflow:

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

Expected validation focus:

```text
python tools/validate_etf_eu_output_contract.py --output-dir output --require-production-dutch-first --report-suffix "$ETF_EU_REPORT_SUFFIX"
python tools/validate_etf_eu_pricing_surface.py "output/weekly_etf_eu_review_${ETF_EU_REPORT_SUFFIX}.md" --require-production-dutch-first
python tools/validate_etf_eu_pricing_surface.py "output/weekly_etf_eu_review_nl_${ETF_EU_REPORT_SUFFIX}.md" --require-production-dutch-first
python tools/validate_etf_eu_fundability_surface.py "output/weekly_etf_eu_review_${ETF_EU_REPORT_SUFFIX}.md"
python tools/validate_etf_eu_fundability_surface.py "output/weekly_etf_eu_review_nl_${ETF_EU_REPORT_SUFFIX}.md"
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
