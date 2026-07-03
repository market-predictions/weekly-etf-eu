# Weekly ETF EU Review OS — Current State

## Snapshot date

2026-07-03

## Repository identity

```text
market-predictions/weekly-etf-eu
```

## Current phase

```text
Phase 9 — EU product assembly via donor-port strategy
```

## Core boundary

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery=false
candidate_promotion=false
```

## Strategic authority

`weekly-etf-eu` remains the EU/UCITS source-of-truth repo. `weekly-etf` remains a donor for mature implementation patterns only.

```text
Port behavior, not U.S. assumptions.
```

## Closed packages

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
WP14A
WP14B
WP14C
WP14D
WP14E
WP14E-FIX
WP14F
WP14G
WP14H
WP14I
WP14J
WP14K
WP14L
WP14M
WP14N
WP14O
WP14P
WP14Q
WP14R
WP14S
WP14T
WP14U
WP14V_SKIP_AND_WP15A_CONTROL_REDIRECT
WP15A
WP15B
WP15C
WP15D
WP15E
WP15F
WP15G
WP15H
ETF-EU-WP15I
ETF-EU-WP15I-RECONCILE
ETF-EU-WP15J
ETF-EU-WP15K
ETF-EU-WP15L
ETF-EU-WP15M
ETF-EU-WP15N
ETF-EU-WP15O
ETF-EU-WP15P
ETF-EU-WP15Q
ETF-EU-WP15R
ETF-EU-WP15S
ETF-EU-WP15T
ETF-EU-WP15U
ETF-EU-WP15V
ETF-EU-WP15W
ETF-EU-WP15X
ETF-EU-WP15Y
```

## Latest completed package — ETF-EU-WP15Y

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15Y
legacy_work_package_id=WP15Y
status=completed
source_work_package=ETF-EU-WP15X
evidence_acquisition_contract=control/ETF_EU_COCKPIT_PDF_READINESS_EVIDENCE_ACQUISITION_CONTRACT_V1.md
closing_price_poc_runner=runtime/fetch_etf_eu_closing_price_poc.py
closing_price_poc_artifact=output/client_surface/etf_eu_closing_price_poc_20260703_000000.json
closing_price_poc_preview=output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md
closing_price_poc_notes=output/client_surface/etf_eu_readiness_evidence_acquisition_contract_notes_20260703_000000.md
closing_price_poc_validator=tools/validate_etf_eu_closing_price_poc.py
closing_price_poc_tests=tests/test_etf_eu_closing_price_poc.py
evidence_acquisition_contract_created=true
closing_price_poc_created=true
closing_price_poc_symbol=SXR8.DE
closing_price_poc_isin=IE00B5BMR087
closing_price_poc_trading_currency=EUR
closing_price_poc_status=failed
pricing_poc_status=failed_provider_or_symbol_unavailable
limited_pricing_poc_performed=true
latest_close_date=null
latest_close=null
provider_error_recorded=true
fake_price_used=false
us_proxy_price_used=false
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
source_pdf_replaced=false
renderer_changed=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
selected_next_package=ETF-EU-WP15Y-FIX
selected_next_package_title=ETF EU closing-price POC provider/symbol repair, no delivery
```

ETF-EU-WP15Y validation package:

```text
validator_added=tools/validate_etf_eu_closing_price_poc.py
tests_added=tests/test_etf_eu_closing_price_poc.py
ci_status=not_visible_in_chatgpt_github_connector
```

## Pricing POC answer

```text
Do we have closing prices now? Not yet.
```

The repo now has SXR8.DE registry-to-pricing wiring, a runner, a machine artifact, a client-readable preview and an explicit provider failure status. It does not yet have a successful latest_close value.

## Active product roadmap

```text
ETF-EU-WP15Y-FIX — ETF EU closing-price POC provider/symbol repair, no delivery
```

## Immediate next action

Start ETF-EU-WP15Y-FIX.

Goal:

```text
Repair the pricing provider or symbol mapping until the system can produce one real SXR8.DE closing-price POC artifact.
```
