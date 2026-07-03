# ETF-EU-WP15Y closing-price POC notes

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15Y
legacy_work_package_id=WP15Y
status=completed_after_closing_price_poc_attempt
evidence_acquisition_contract=control/ETF_EU_COCKPIT_PDF_READINESS_EVIDENCE_ACQUISITION_CONTRACT_V1.md
closing_price_poc_runner=runtime/fetch_etf_eu_closing_price_poc.py
closing_price_poc_artifact=output/client_surface/etf_eu_closing_price_poc_20260703_000000.json
closing_price_poc_preview=output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md
closing_price_poc_symbol=SXR8.DE
closing_price_poc_isin=IE00B5BMR087
provider_status=failed
pricing_poc_status=failed_provider_or_symbol_unavailable
selected_next_package=ETF-EU-WP15Y-FIX
```

## Do we have closing prices now?

Before WP15Y:

```text
No committed closing-price artifact existed.
```

After WP15Y:

```text
A limited SXR8.DE closing-price POC artifact exists, but the provider attempt failed in this execution environment.
```

So the current answer is:

```text
No successful close value yet. The repo now has the wiring, runner, artifact shape and preview surface, but not a successful provider result.
```

## What was proven

```text
ISIN=IE00B5BMR087
exchange=Xetra
exchange_ticker=SXR8
trading_currency=EUR
pricing_symbol=SXR8.DE
```

## Failure status

```text
provider_status=failed
pricing_poc_status=failed_provider_or_symbol_unavailable
latest_close=null
```

No fake price was inserted and no U.S. proxy price was used.

## Boundary confirmation

```text
limited_pricing_poc_performed=true
valuation_grade=false
pricing_evidence_for_client_grade=false
pricing_evidence_for_delivery_preflight=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
delivery_preflight_allowed=false
receipt_artifact_created=false
production_manifest_created=false
source_pdf_replaced=false
renderer_changed=false
```

## Recommended next package

```text
ETF-EU-WP15Y-FIX — ETF EU closing-price POC provider/symbol repair, no delivery
```
