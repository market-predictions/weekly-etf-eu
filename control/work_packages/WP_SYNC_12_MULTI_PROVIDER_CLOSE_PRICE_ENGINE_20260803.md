# ETF-EU-WP-SYNC-12 — Multi-Provider Completed-Close Engine

## Priority

```text
CRITICAL_INPUT_STATE_BLOCKER
```

Fresh, exact-line completed closing prices are required before the Weekly ETF EU report can be considered useful. This package takes priority over routine delivery promotion.

## Current issue

- Stooq is blocked by browser verification on GitHub-hosted runners.
- Yahoo/yfinance is intermittently throttled and performs more requests than necessary.
- The routine path lacks a deterministic provider qualification layer and exact-line evidence matrix.

## Root cause

The existing pricing implementation combines provider transport, symbol resolution, completed-close selection and fallback behavior in one narrow adapter. Provider-specific authentication, schemas, quotas and exact trading-line identities are not normalized into one contract.

## Decision framework

- Development-stage pricing may use free API plans and public endpoints.
- No provider is promoted solely because it returns a number.
- The engine accepts only a positive finite close dated on or before the requested report date.
- Exact venue, currency and trading-line identity remain explicit evidence fields.
- Provider disagreement is retained as evidence; it is not silently averaged.
- No portfolio mutation, allocation decision or report delivery authority is granted.

## Input/state contract

Provider chain:

1. Leeway (`LEEWAY_API_TOKEN`)
2. EODHD (`EODHD_API_TOKEN`)
3. Marketstack (`MARKETSTACK_API_KEY`)
4. Alpha Vantage (`ALPHA_VANTAGE_API_KEY`)
5. Yahoo direct chart endpoint (no key)

Twelve Data is intentionally deferred.

Each provider adapter must return the normalized contract:

```text
provider_id
provider_symbol
requested_report_date
pricing_status
close_date
close_price
currency
exchange_or_mic
http_status
response_classification
observed_at_utc
blockers
```

## Output contract

Required outputs:

- one row per basket line and provider attempt;
- one selected completed close per line when available;
- provider coverage summary;
- funded-position coverage gate;
- cross-provider agreement evidence where at least two providers succeed;
- no secret values in logs or artifacts.

## Operational runbook

1. Implement provider adapters behind one interface.
2. Add provider-specific symbols to the controlled basket where required.
3. Add a no-send GitHub Actions qualification workflow.
4. Run the engine with all configured secrets; missing secrets are explicit skips.
5. Validate Yahoo direct immediately as the zero-secret control provider.
6. Add secrets one provider at a time and rerun qualification.
7. Promote a provider only after exact-line and completed-close checks pass.
8. Integrate the selected engine into the routine valuation overlay.

## Exact files

- `pricing/provider_close_price_engine.py`
- `pricing/build_multi_provider_close_price_results.py`
- `config/ucits_close_price_validation_basket.yml`
- `.github/workflows/probe-multi-provider-close-prices.yml`
- `tests/test_provider_close_price_engine.py`
- `control/claims/CLAIM_WP_SYNC_12_MULTI_PROVIDER_CLOSE_PRICE_ENGINE_20260803.md`

## Authority boundaries

```text
portfolio_mutation=false
ledger_write=false
allocation_authority=false
delivery_authority=false
licensing_promotion=false
```
