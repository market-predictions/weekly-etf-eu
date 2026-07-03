# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-WP15Y-FIX — ETF EU closing-price POC provider/symbol repair, no delivery**.

## Adopted strategy

```text
Keep market-predictions/weekly-etf-eu as the EU/UCITS source-of-truth repo.
Use market-predictions/weekly-etf as an upstream donor for mature implementation layers.
Port behavior, not U.S. assumptions.
Use namespaced workpackage IDs in all repo, branch, PR, artifact and handover communication.
```

## Completed through latest package

```text
ETF-EU-WP15V
ETF-EU-WP15W
ETF-EU-WP15X
ETF-EU-WP15Y
```

## ETF-EU-WP15Y completion evidence

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15Y
legacy_work_package_id=WP15Y
status=completed
evidence_acquisition_contract=control/ETF_EU_COCKPIT_PDF_READINESS_EVIDENCE_ACQUISITION_CONTRACT_V1.md
closing_price_poc_runner=runtime/fetch_etf_eu_closing_price_poc.py
closing_price_poc_artifact=output/client_surface/etf_eu_closing_price_poc_20260703_000000.json
closing_price_poc_preview=output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md
closing_price_poc_validator=tools/validate_etf_eu_closing_price_poc.py
closing_price_poc_tests=tests/test_etf_eu_closing_price_poc.py
closing_price_poc_symbol=SXR8.DE
closing_price_poc_isin=IE00B5BMR087
closing_price_poc_status=failed
pricing_poc_status=failed_provider_or_symbol_unavailable
limited_pricing_poc_performed=true
latest_close=null
fake_price_used=false
us_proxy_price_used=false
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
selected_next_package=ETF-EU-WP15Y-FIX
```

## Active next package

```text
ETF-EU-WP15Y-FIX — ETF EU closing-price POC provider/symbol repair, no delivery
```

Purpose:

```text
Repair the pricing provider or symbol mapping until the system can produce one real SXR8.DE closing-price POC artifact.
```

## Likely inputs for ETF-EU-WP15Y-FIX

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
config/ucits_symbol_registry.yml
runtime/fetch_etf_eu_closing_price_poc.py
output/client_surface/etf_eu_closing_price_poc_20260703_000000.json
output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md
tools/validate_etf_eu_closing_price_poc.py
```

ETF-EU-WP15Y-FIX should create or update:

```text
provider/symbol repair artifact
updated closing-price POC artifact
updated closing-price POC preview
validator/test updates if needed
updated control state after validation
```

## Boundary remains

```text
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

## Do not do next

Do not use fake prices.
Do not use U.S. proxy prices as EU UCITS prices.
Do not mutate portfolio state.
Do not promote candidates.
Do not create funding authority.
Do not create valuation-grade authority.
Do not change ETF recommendation logic.
Do not rebuild or replace the WP15T PDF.
