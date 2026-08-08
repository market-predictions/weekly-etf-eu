# WP-SYNC-11A operational reopen audit — 2026-08-08

## Status

```text
work_package=ETF-EU-WP-SYNC-11A
previous_status=CLOSED_VALIDATED
current_status=REOPENED_OPERATIONALIZATION
reason=validated July 31 three-position architecture did not prove future-date four-position provider redundancy
portfolio_mutation=false
ledger_write=false
delivery_authority=false
```

## Material findings

The original closeout remains valid as a development-model proof for report date 2026-07-31 and the then-current three funded positions. It is not sufficient evidence that the five-provider architecture is operational for later report dates.

Fresh isolated live audit run `31255211953` tested report date `2026-08-05` without historical cache reuse. The deterministic WP11A suite passed and the live provider matrix completed, but the enforced current-four-position readiness verdict failed.

Provider availability observed in the isolated run:

```text
leeway=not_configured_missing_LEEWAY_API_TOKEN
eodhd=not_configured_missing_EODHD_API_TOKEN
marketstack=not_configured_missing_MARKETSTACK_ACCESS_KEY
alpha_vantage=disabled_by_secret_safety_pending_confirmed_key_rotation
yahoo_chart=live
```

Yahoo Chart returned exact 2026-08-05 Xetra/EUR closes for VWCE, EUNA, SXR8 and L0CK. With no second live provider, all four lines were `single_source_only`.

The live audit artifact is:

```text
workflow_run=31255211953
artifact_id=9021200763
artifact_sha256=02d80ccc11900f569f70b0abe58a978ea884063ad4e7e144c50085405bd1e649
```

## Input/state contract defect

`config/ucits_price_provider_registry.yml` still declared L0CK `funded: false` while the authoritative portfolio state contains four `funded_model_position` rows: VWCE, EUNA, SXR8 and L0CK.

Static registry funding flags are therefore no longer authoritative. The repaired pricing path derives the funded universe from `output/etf_eu_portfolio_state.json` using exact ISIN+ticker+primary-exchange+trading-currency identity. A funded portfolio line without exactly one provider-registry match fails closed.

## Closure criteria for the reopened operationalization

WP-SYNC-11A may return to `CLOSED_VALIDATED` only after all of the following are true on the current release candidate:

1. deterministic adapter, cache, redaction, consensus, identity, funded-universe, valuation and client-surface tests pass;
2. the live qualification artifact derives four funded lines from authoritative portfolio state;
3. no historical close cache is required for the target report date;
4. all four funded positions have at least two same-date providers within the 1.0% spread gate;
5. each funded consensus has at least one exact-line symbol/venue/currency identity anchor;
6. protected portfolio and ledger state remain unchanged;
7. the proven multi-provider qualification path is the pricing path used by the governed routine production flow;
8. independent governance release assurance is rerun for the repaired candidate before merge or delivery.
