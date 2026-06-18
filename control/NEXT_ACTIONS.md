# Weekly ETF EU Review OS — Next Actions

Current priority: **port mature report/runtime/bilingual/report-quality safeguards from `weekly-etf` into `weekly-etf-eu`, without importing U.S. portfolio truth**.

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
WP14F
```

## WP14F completion evidence

```text
first_etf_eu_draft_report_created=true
report_output_path=output/weekly_etf_eu_review_260618_draft.md
pricing_artifact_used=output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json
pricing_symbols_included=CSPX.L,SXR8.DE
review_only=true
production_delivery=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
selected_next_package=WP14G
```

Validation evidence supplied from Codespaces:

```text
ETF_EU_UCITS_CLOSING_PRICE_SMOKE_OK: attempted=2 prices_found=2 skipped=3 source_errors=0 selected_next_package=WP14F
ETF_EU_DRAFT_REPORT_SURFACE_OK: output/weekly_etf_eu_review_260618_draft.md
tests/test_etf_eu_draft_report_surface.py: 5 passed
tests/test_etf_eu_ucits_closing_price_smoke.py: 30 passed
tests/test_etf_eu_ucits_symbol_registry_identity.py: 20 passed
tests/test_etf_eu_wp14c_ucits_identity_audit.py: 34 passed
tests/test_etf_eu_wp14b_roadmap_lane_implementation_plan.py: 36 passed
tests/test_etf_eu_wp14a_roadmap_lane_selection.py: 32 passed
```

No PDF, email, recipient activation, production delivery, portfolio mutation, candidate promotion, funding authority, or valuation-grade authority occurred.

## Active next package

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

WP14G must not:

```text
reuse U.S. ETF holdings as EU holdings
present U.S. tickers as EU investable instruments
mutate portfolio state
promote candidates to fundable
claim valuation-grade authority
generate production PDFs
send email
activate recipients
claim production delivery
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
runtime/bilingual donor-port
pricing artifact integration into mature report state
shadow PDF/render dry run
```
