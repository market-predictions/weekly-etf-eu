# ETF-EU-WP15AA-FIX multi-line pricing universe repair notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15AA-FIX
source_work_package=ETF-EU-WP15AA
repair_status=success
repair_target=CSPX.L
successful_second_line_symbol=CSPX.L
successful_second_line_isin=IE00B5BMR087
successful_second_line_close_date=2026-07-03
successful_second_line_close=807.859985
successful_second_line_pricing_source=yahoo_chart_v8
successful_rows_count=2
failed_rows_count=0
skipped_rows_count=1
selected_next_package=ETF-EU-WP15AB
```

## Result

CSPX.L was repaired as the second successful EU trading-line price using the Yahoo chart provider from Codespaces.

The cockpit preview now has two successful rows: SXR8.DE and CSPX.L. SMH remains skipped because its Yahoo pricing symbol is still pending verification.

## Boundary

No fake price, U.S. proxy price, funding, portfolio mutation, candidate promotion, valuation-grade claim, or delivery path was created.
