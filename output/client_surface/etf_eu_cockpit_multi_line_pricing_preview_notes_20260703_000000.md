# ETF-EU-WP15AA multi-line pricing preview notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15AA
source_work_package=ETF-EU-WP15Z
multi_line_pricing_preview_created=true
successful_rows_count=1
failed_rows_count=0
skipped_rows_count=2
mandatory_sxr8_success=true
pdf_created=false
selected_next_package=ETF-EU-WP15AA-FIX
```

## Result

The preview now has a multi-line pricing structure.

SXR8.DE is the only successful price row:

```text
SXR8.DE | IE00B5BMR087 | 2026-07-03 | 706.119995 | yahoo_chart_v8 | success
```

CSPX.L is present in the registry but remains skipped because the pricing pipeline is still pending. SMH remains skipped because the provider symbol is still pending verification.

## Interpretation

This package proves the cockpit can separate successful, skipped and pending EU trading lines without using U.S. proxies or fake prices.

It does not yet prove a two-line successful pricing universe. The correct next package is therefore ETF-EU-WP15AA-FIX.
