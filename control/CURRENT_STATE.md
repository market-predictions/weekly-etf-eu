# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-08
repository=market-predictions/weekly-etf-eu
working_branch=agent/etf-eu-governed-release-20260805
pull_request=78
operating_mode=ROUTINE_WEEKLY_ETF_EU_PRODUCTION_WITH_INDEPENDENT_RELEASE_ASSURANCE
current_work_package=ETF-EU-WP-SYNC-11A_OPERATIONALIZATION_20260808
state=BLOCKED_EXTERNAL_CREDENTIAL
principal_decision_required=false
principal_action_required=ROTATE_ALPHA_VANTAGE_REPOSITORY_SECRET
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

## Current objective

Finish operationalizing the already validated WP-SYNC-11A multi-provider completed-close architecture for the current four-position model portfolio, then rerun the governed fresh-package and independent-assurance path without weakening the pricing gate.

The relevant distinction is now explicit:

- the WP11A **software architecture** is validated;
- the WP11A **fresh-date operational provider redundancy** is not yet complete;
- the remaining pricing blocker is an external provider credential boundary, not a need for a new pricing architecture.

## Authoritative protected portfolio

Authority:

```text
output/etf_eu_portfolio_state.json
```

Current funded model positions:

| Ticker | ISIN | Venue | Shares |
|---|---|---|---:|
| VWCE | IE00BK5BQT80 | Xetra | 151 |
| EUNA | IE00BDBRDM35 | Xetra | 1,526 |
| SXR8 | IE00B5BMR087 | Xetra | 10 |
| L0CK | IE00BG0J4C88 | Xetra | 934 |

```text
funded_position_count=4
model_portfolio_only=true
real_broker_execution=false
```

## WP11A funded-universe repair

The provider registry previously contained historical `funded` flags and still declared `L0CK` unfunded after the portfolio had activated it. That duplication is no longer pricing authority.

The repaired qualification path now derives the funded universe from `output/etf_eu_portfolio_state.json` and matches every funded line to the provider registry by:

```text
ISIN + ticker + primary_exchange + trading_currency
```

A funded portfolio position without exactly one registry match fails closed. Stale static registry flags are surfaced only as diagnostics.

Implementation:

```text
pricing/ucits_funded_universe.py
pricing/build_ucits_close_price_validation_basket_results.py
tools/qualify_ucits_price_providers.py
tests/test_ucits_funded_universe.py
```

The deterministic funded-universe regression tests pass on PR #78.

## Fresh no-cache live evidence — 2026-08-05

Repaired isolated audit:

```text
workflow_run=31258172996
artifact_id=9022002190
artifact_sha256=c91db0567da886eb83f4c1dbf67e44a5604da107ed92b4f543e1fa980153786b
funded_line_count=4
funded_identity_anchors=4/4
funded_consensus=0/4
historical_cache_used=0
pricing_gate_passed=false
protected_state_unchanged=true
```

Provider availability observed:

```text
leeway=not_configured_missing_LEEWAY_API_TOKEN
eodhd=not_configured_missing_EODHD_API_TOKEN
marketstack=not_configured_missing_MARKETSTACK_ACCESS_KEY
alpha_vantage=secret_present_but_disabled_pending_confirmed_rotation
yahoo_chart=live
```

Yahoo Chart returned exact 2026-08-05 Xetra/EUR closes for all four funded lines and supplied the required identity anchor, but a single source cannot satisfy the two-provider gate.

## Production-path convergence

The canonical routine workflow already used `pricing/build_ucits_close_price_validation_basket_results.py`. The PR #78 fresh-package path previously bypassed that engine through the old current-session compatibility route.

That divergence is repaired. The PR fresh-package runner now routes the historical entry point through:

```text
pricing/build_wp11a_current_session_compat.py
→ pricing/build_ucits_close_price_validation_basket_results.py
```

Regression protection:

```text
tests/test_run_etf_eu_aug3_expanded_report_v6_pricing_route.py
```

Fresh governed-package run:

```text
workflow_run=31258280491
source_sha=c7c4932fb9fdef7f2836d23273eb10405613d4eb
routing_tests=PASS
wp11a_route_observed=true
funded_consensus=0/4
funded_identity_anchors=4/4
historical_cache_used=0
stale_registry_flag_detected=l0ck_xetra_eur
alpha_vantage_live=false
terminal_result=FAIL_CLOSED_AT_WP11A_PRICE_GATE
```

This is the intended fail-closed result until a second provider is genuinely live. The prior Börse/Yahoo compatibility path is no longer production authority for this release candidate.

## External credential blocker

Alpha Vantage is the shortest second-provider path because:

1. its adapter is already implemented and deterministically tested;
2. a repository secret already exists;
3. prior accepted July 31 evidence demonstrated Alpha Vantage + Yahoo agreement for VWCE, EUNA and SXR8;
4. live use is deliberately disabled by `pricing/provider_secret_safety.py` because the earlier key may have been exposed in a provider response message.

The existing secret must therefore be replaced with a newly issued Alpha Vantage key. Only after the principal confirms replacement may the repository record `config/alpha_vantage_key_rotation_confirmed.json` and re-enable the provider.

If Alpha Vantage cannot return valid same-date exact-line evidence for all four funded positions, the next fallback is to configure one of Leeway, EODHD or Marketstack; the two-provider requirement will not be relaxed.

## WP11A closure criteria

WP-SYNC-11A operationalization may close only when the exact release candidate proves:

```text
funded_universe_authority=output/etf_eu_portfolio_state.json
funded_position_count=4
same_date_provider_requirement=2
agreement_tolerance_pct=1.0
historical_cache_required=false
funded_consensus=4/4
funded_identity_anchors=4/4
protected_state_unchanged=true
fresh_package_uses_wp11a_engine=true
independent_release_assurance=PASS
```

## Authority boundary

No fresh report has been delivered in this work cycle. No portfolio or ledger mutation occurred. No real broker execution occurred. A successful future pricing run will still not itself constitute report delivery or production closeout.
