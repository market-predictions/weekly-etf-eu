# ETF-EU-WP-SYNC-11A — Multi-provider completed-close pricing engine

## Priority and current issue

The Weekly ETF EU routine cannot be considered decision-grade while fresh completed-close pricing depends on one opaque, throttled provider. Stooq is blocked by browser verification on GitHub-hosted runners and Yahoo/yfinance has shown variable rate-limit behavior.

This package has priority over report rendering and delivery work. Report generation must not continue when the three funded trading lines lack defensible completed closes.

## Upstream donor assessment

The closest mature `market-predictions/weekly-etf` donor is the portfolio close-first review. It provides useful freshness and close-first gate concepts, but it is Yahoo-only and ticker-first. The EU implementation therefore adapts the gate and evidence pattern rather than copying the provider implementation.

## Decision framework

- Use development-only free allowances to establish a working pricing model.
- Qualify Leeway first, EODHD second, Marketstack third, Alpha Vantage fourth and Yahoo Chart as the unkeyed control fallback.
- Require at least two providers to agree on the same completed-close date for every funded line before the routine report pricing gate passes.
- Require at least one agreeing provider to return matching symbol, venue and currency metadata.
- Reject stale, non-positive, wrong-currency and wrong-venue results.
- Keep provider licensing separate from technical qualification; no provider is promoted to production or redistribution authority in this package.

## Input/state contract

Authoritative identity remains ISIN-first and exact-line specific:

```text
config/ucits_price_provider_registry.yml
```

Every row records:

- ISIN;
- expected MIC/venue;
- expected currency;
- exact provider symbol;
- provider exchange code;
- funded-position status.

Secrets are read only from:

```text
LEEWAY_API_TOKEN
EODHD_API_TOKEN
MARKETSTACK_ACCESS_KEY
ALPHA_VANTAGE_API_KEY
```

Yahoo Chart requires no secret. Secret values and provider response bodies must never be written to artifacts or logs.

## Output contract

The qualification artifact must contain:

- all 12 controlled trading lines;
- a result per configured provider and line;
- identity status and sanitized identity evidence;
- completed-close date and price;
- returned currency and venue where available;
- freshness and blocker classifications;
- same-date provider agreement;
- median consensus close;
- an exact-line metadata anchor;
- a separate funded-position report-pricing gate.

Schema:

```text
ucits_price_provider_qualification_v1
```

The existing routine valuation contract receives a compatibility artifact only after the qualification matrix is generated.

## Operational runbook

1. Run deterministic mocked adapter tests.
2. Run provider identity discovery using ISIN and exchange symbol listings where the API supports it.
3. Fetch completed closes on or before the requested report date.
4. Normalize all provider outputs.
5. Reject identity, currency, venue and freshness failures.
6. Calculate same-date provider agreement and median consensus.
7. Require at least one exact-line metadata anchor inside each funded consensus.
8. Block routine report generation unless all funded lines pass both gates.
9. Persist the qualification artifact and compatibility pricing artifact.
10. Preserve official portfolio and ledger state.

## Provider call-budget design

- Leeway: exchange symbol lists by venue plus 12 close requests; designed to remain within the free development allowance.
- EODHD: exchange symbol lists by venue plus 12 close requests; designed to remain within the 20-call daily free allowance.
- Marketstack: ISIN search plus close requests during qualification; routine runs skip repeated identity discovery.
- Alpha Vantage: 12 symbol searches plus 12 daily-series requests during qualification; routine runs skip repeated identity discovery.
- Yahoo Chart: one direct chart request per line, with bounded query1/query2 fallback.
- Pull-request validation is deterministic only; quota-consuming live qualification is manual or part of an explicitly requested routine preview.
- Accepted historical evidence can be reused only for an exact report date, basket ID, provider and provider symbol, with immutable artifact provenance.

## Security and evidence controls

A provider quota response echoed the Alpha Vantage API key in its message body during early qualification. The implementation now:

- stores provider classifications only, never provider response-message bodies;
- strips common credential fields from identity evidence;
- tests redaction deterministically;
- purged fourteen pre-redaction GitHub Actions artifacts;
- requires rotation of the Alpha Vantage key before future live use.

The accepted 2026-07-31 funded-price evidence is separately persisted in:

```text
config/etf_eu_provider_close_cache_20260731.json
```

It is development-only and automatically ignored for any other report date.

## Current validated pricing result

The development engine has produced same-date Alpha Vantage and direct Yahoo Chart consensus for all three funded positions on 2026-07-31:

| Position | Alpha Vantage | Yahoo Chart | Consensus | Spread |
|---|---:|---:|---:|---:|
| VWCE | €162.96000000 | €162.96000671 | €162.96000335 | 0.000004% |
| EUNA | €4.88000000 | €4.88000011 | €4.88000006 | 0.000002% |
| SXR8 | €696.24000000 | €696.23999023 | €696.23999512 | 0.000001% |

```text
funded_price_consensus=3/3
funded_identity_anchors=3/3
valuation_overlay_nav_eur=99455.68
portfolio_mutation=false
ledger_write=false
delivery_authority=false
```

Leeway, EODHD and Marketstack adapters are implemented but remain `not_configured` until their repository secrets are added.

## Acceptance criteria

- Adapter unit tests pass.
- Cache, redaction, consensus and identity-anchor tests pass.
- Qualification workflow produces exactly 12 lines and 3 funded lines.
- No secret appears in logs or artifacts.
- Yahoo Chart is tested independently of yfinance.
- Missing keys are classified as `not_configured`, not as missing prices.
- Funded consensus requires at least two providers on the same date within 1.0% spread.
- Funded consensus requires at least one matching symbol/venue/currency metadata anchor.
- Existing report workflow is blocked when funded consensus is absent.
- No portfolio mutation, ledger write, delivery or recipient action occurs.

## Current status

```text
status=IMPLEMENTED_AND_PRICING_VALIDATED
pricing_stage=PASS
macro_adapter=PASS
macro_validator=IMPLEMENTED_PENDING_FULL_PREVIEW_RERUN
full_report_preview=IN_PROGRESS
commercial_licensing_review=DEFERRED_BY_USER
```
