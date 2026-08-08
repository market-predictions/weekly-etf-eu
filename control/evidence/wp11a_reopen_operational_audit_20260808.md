# WP-SYNC-11A operational reopen audit — 2026-08-08

## Status

```text
work_package=ETF-EU-WP-SYNC-11A
previous_status=CLOSED_VALIDATED
current_status=REOPENED_OPERATIONALIZATION_BLOCKED_EXTERNAL_CREDENTIAL
reason=validated July 31 three-position architecture did not prove future-date four-position provider redundancy
portfolio_mutation=false
ledger_write=false
delivery_authority=false
```

## Original closure interpretation

The original WP-SYNC-11A closeout remains valid as a development-model proof for report date `2026-07-31` and the then-current three funded positions. It does not establish that fresh-date provider redundancy is operational for later portfolio states.

Its historical evidence explicitly required a fresh second provider for future report dates.

## First isolated live audit

Fresh isolated live audit run `31255211953` tested report date `2026-08-05` without historical cache reuse. The deterministic WP11A suite passed and the live provider matrix completed, but the current-four-position readiness verdict failed.

Provider availability observed:

```text
leeway=not_configured_missing_LEEWAY_API_TOKEN
eodhd=not_configured_missing_EODHD_API_TOKEN
marketstack=not_configured_missing_MARKETSTACK_ACCESS_KEY
alpha_vantage=disabled_by_secret_safety_pending_confirmed_key_rotation
yahoo_chart=live
```

Yahoo Chart returned exact 2026-08-05 Xetra/EUR closes for VWCE, EUNA, SXR8 and L0CK. With no second live provider, all four lines were `single_source_only`.

```text
workflow_run=31255211953
artifact_id=9021200763
artifact_sha256=02d80ccc11900f569f70b0abe58a978ea884063ad4e7e144c50085405bd1e649
```

## Input/state contract defect and repair

`config/ucits_price_provider_registry.yml` still declared L0CK `funded: false` while the authoritative portfolio state contains four `funded_model_position` rows: VWCE, EUNA, SXR8 and L0CK.

Static registry funding flags are no longer pricing authority. The repaired pricing path derives the funded universe from:

```text
output/etf_eu_portfolio_state.json
```

Exact match contract:

```text
ISIN + ticker + primary_exchange + trading_currency
```

A funded portfolio line without exactly one provider-registry match fails closed. Static registry flags are retained only as diagnostics.

Implementation:

```text
pricing/ucits_funded_universe.py
pricing/build_ucits_close_price_validation_basket_results.py
tools/qualify_ucits_price_providers.py
tests/test_ucits_funded_universe.py
```

## Repaired four-position live audit

A second isolated run exercised the repaired state contract with historical provider cache disabled.

```text
workflow_run=31258172996
artifact_id=9022002190
artifact_sha256=c91db0567da886eb83f4c1dbf67e44a5604da107ed92b4f543e1fa980153786b
funded_line_count=4
funded_tickers=VWCE,EUNA,SXR8,L0CK
funded_consensus_count=0
funded_identity_anchor_count=4
historical_cache_used=0
stale_registry_funded_flags_overridden=l0ck_xetra_eur
report_pricing_gate_passed=false
protected_state_unchanged=true
```

Every deterministic WP11A test, the authoritative four-position contract check, evidence upload and protected-state proof passed. The workflow failed only at the final operational-readiness assertion because all four funded lines still had only Yahoo as a live provider.

Secret-safety observation:

```text
alpha_vantage_secret_was_present=true
alpha_vantage_rotation_confirmed=false
alpha_vantage_live_enabled=false
```

The secret-safety control is therefore working as designed.

## Fresh-package production-path convergence

Before this repair, the canonical routine workflow used WP11A but PR #78's special fresh-package runner inherited an older current-session pricing route. That meant the release candidate and post-merge routine could test different pricing systems.

The PR fresh-package route now converges through:

```text
pricing/build_wp11a_current_session_compat.py
→ pricing/build_ucits_close_price_validation_basket_results.py
```

Regression test:

```text
tests/test_run_etf_eu_aug3_expanded_report_v6_pricing_route.py
```

Observed fresh-package evidence:

```text
workflow_run=31258280491
source_sha=c7c4932fb9fdef7f2836d23273eb10405613d4eb
routing_and_state_tests=8_passed
observed_pricing_entrypoint=pricing/build_wp11a_current_session_compat.py
observed_canonical_builder=pricing/build_ucits_close_price_validation_basket_results.py
funded_consensus=0/4
funded_identity_anchors=4/4
historical_cache_used=0
stale_registry_flags=l0ck_xetra_eur
alpha_vantage_live=false
terminal_result=FAIL_CLOSED_AT_WP11A_PRICE_GATE
diagnostics_artifact_id=9022036048
diagnostics_artifact_sha256=e477ef751905818a51f578bcbc51c83b4676b4e9c2e37cce177b1dfea3b31349
```

This proves the prior Börse/Yahoo compatibility path is no longer the pricing authority for the PR #78 fresh-package flow.

## Current external dependency

Alpha Vantage is the shortest second-provider path. Its adapter is implemented and tested, the repository already contains an Alpha Vantage secret, and accepted July 31 evidence previously showed Alpha/Yahoo agreement for VWCE, EUNA and SXR8.

The existing secret must be replaced because an earlier provider response may have exposed it. `pricing/provider_secret_safety.py` intentionally removes the live key from the process until a non-secret rotation confirmation marker exists.

Do not create that marker until the principal confirms that the GitHub Actions repository secret `ALPHA_VANTAGE_API_KEY` has actually been replaced.

If the rotated Alpha Vantage key does not produce usable same-date evidence for all four funded lines, keep the price gate closed and proceed to Leeway, EODHD or Marketstack rather than weakening the contract.

## Closure criteria for the reopened operationalization

WP-SYNC-11A may return to `CLOSED_VALIDATED` only after all of the following are true on the exact release candidate:

1. deterministic adapter, cache, redaction, consensus, identity, funded-universe, valuation and client-surface tests pass;
2. the live qualification artifact derives four funded lines from authoritative portfolio state;
3. no historical close cache is required for the target report date;
4. all four funded positions have at least two same-date providers within the 1.0% spread gate;
5. each funded consensus has at least one exact-line symbol/venue/currency identity anchor;
6. protected portfolio and ledger state remain unchanged;
7. the same WP11A multi-provider qualification path is used by PR fresh-package validation and canonical routine production;
8. independent governance release assurance is rerun for the repaired candidate before merge or delivery.
