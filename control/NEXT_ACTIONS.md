# Weekly ETF EU Review OS — Next Actions

Current priority: **product assembly, not recloning and not another control-loop package**.

## Adopted strategy

```text
Keep market-predictions/weekly-etf-eu as the EU/UCITS source-of-truth repo.
Use market-predictions/weekly-etf as an upstream donor for mature report/runtime/bilingual/macro/delivery safeguards.
Port mature layers in controlled slices.
Adapt all donor behavior to EU-specific UCITS identity, pricing and investability contracts.
```

Do not fresh-clone `weekly-etf` over `weekly-etf-eu`.

## Completed

```text
WP9
WP10
WP10B
WP11
WP12
WP12B
WP12C
WP12D
WP12E
WP12F
WP13A
WP13B
WP13C
WP13D
WP13E
WP13F
WP13G
WP13H
WP13I
WP14A
WP14B
WP14C
WP14D
WP14E
WP14E-FIX
```

## Pricing status

```text
ucits_closing_price_smoke_completed=true
direct_yahoo_chart_endpoint_validated=true
prices_found=2
pricing_symbols_found=CSPX.L,SXR8.DE
pricing_symbols_attempted=2
symbols_skipped=3
source_errors=0
selected_next_package=WP14F
```

This proves first UCITS closing-price source feasibility for the tested exchange-line symbols.

It does not grant:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
wp14_authority=false
```

## Active next package

```text
WP14F — First ETF EU draft report from UCITS identity and closing-price smoke data, review-only
```

Purpose:

```text
produce the first markdown EU ETF report draft from real UCITS identity and pricing artifacts
```

WP14F must use:

```text
config/ucits_symbol_registry.yml
output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json
```

WP14F must visibly disclose:

```text
UCITS identity
ISIN
exchange ticker
trading currency
Yahoo chart source symbol
latest close date
latest close
U.S. proxy labels as research-only
source/freshness limitations
```

WP14F must not:

```text
send reports
generate production PDFs
activate recipients
mutate portfolio state
promote candidates to fundable
claim valuation-grade authority
claim production delivery
```

## Next planned package after WP14F

```text
WP14G — Port weekly-etf runtime/bilingual/report-quality layers into weekly-etf-eu
```

Purpose:

```text
bring mature weekly-etf report/runtime/bilingual/report-quality safeguards into the EU repo without importing U.S. portfolio truth
```

Likely donor layers from `market-predictions/weekly-etf`:

```text
runtime/render_etf_report_from_state.py
runtime/polish_runtime_reports.py
runtime/link_runtime_report_tickers.py
runtime/delivery_html_overrides.py
etf-pro.txt
etf-pro-nl.txt
bilingual parity tests
Dutch language quality validators
macro/report-surface leakage validators
report decision clarity tests
```

Rule:

```text
Port behavior, not U.S. assumptions.
```

## Later package

```text
WP14H — ETF EU delivery/PDF dry run, no recipients
```

Delivery remains blocked until:

```text
EU markdown report quality passes
bilingual parity gates pass
Dutch language gates pass
UCITS pricing/freshness disclosure is stable
PDF/HTML dry run passes
recipient policy exists
secrets policy exists
real delivery receipt/manifest path exists
explicit control-layer delivery authorization is recorded
```

## Do not do next

Do not create another abstract Stage-2 or review-only package unless it directly unblocks one of:

```text
first EU report draft
runtime/bilingual donor-port
pricing artifact integration
shadow PDF/render dry run
```
