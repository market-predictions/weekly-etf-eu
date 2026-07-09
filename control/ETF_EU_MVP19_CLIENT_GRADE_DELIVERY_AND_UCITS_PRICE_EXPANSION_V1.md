# ETF-EU-MVP19 client-grade delivery and UCITS price expansion v1

## Purpose

MVP19 redirects the post-transport work from receipt closeout to delivery-package quality. The previous controlled run proved transport only; it did not prove client-grade package quality.

## Reference rule

```text
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

## Decision framework

Use weekly-etf for architecture and format patterns only. Use EU/UCITS instruments for all investable identity, price and client-surface facts.

## Input/state contract

Required EU inputs are UCITS identity, ISIN, exchange line, ticker, currency, close-price source, and source-quality status.

## Output contract

Dutch-first client package must be PDF/HTML-ready, not Markdown-only. U.S. proxy tickers must not appear as investable EU candidates. Stale non-delivery wording must not appear in a sent package.

## Operational runbook

Expand UCITS close-price coverage, validate client package quality, then only resend after PDF and package gates pass.

## MVP19 result

```text
client_grade_package_ready=false
ucits_close_price_validation_basket_created=true
ucits_close_price_validation_basket_path=config/ucits_close_price_validation_basket.yml
pdf_output_available=false
stale_delivery_wording_detected=true
main_surface_us_proxy_exposure_detected=true
readiness_status=ucits_pricing_or_package_hardening_required
selected_next_package=ETF-EU-MVP19-FIX
```
