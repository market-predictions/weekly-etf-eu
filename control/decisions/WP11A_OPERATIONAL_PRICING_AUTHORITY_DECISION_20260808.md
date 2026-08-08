# WP11A operational pricing authority decision — 2026-08-08

## Status

```text
decision_id=WP11A_OPERATIONAL_PRICING_AUTHORITY_20260808
status=ADOPTED_ON_RELEASE_CANDIDATE
repository=market-predictions/weekly-etf-eu
pull_request=78
```

## Decision

For Weekly ETF EU completed-close qualification:

1. `output/etf_eu_portfolio_state.json` is authoritative for the current funded model universe.
2. `config/ucits_price_provider_registry.yml` controls exact provider trading-line identity and symbols, but its static `funded` values are not portfolio authority.
3. A funded position must match exactly one provider-registry line by ISIN, ticker, primary exchange and trading currency; missing or ambiguous matches fail closed.
4. The canonical multi-provider qualification engine from WP-SYNC-11A is the sole production pricing-gate architecture for funded completed closes.
5. Both the PR fresh-package release path and the canonical routine path must use the same WP11A qualification engine.
6. The historical Börse/Yahoo current-session compatibility path is not production pricing authority for the current release candidate.
7. Every funded line continues to require at least two providers on the same completed-close date within 1.0% spread and at least one exact-line symbol/venue/currency identity anchor.
8. Historical provider evidence may be reused only under the existing exact-date immutable-provenance cache contract; it cannot be carried forward to a later report date.
9. A provider credential incident requires rotation before that provider is re-enabled. A rotation-confirmation marker may record only non-secret metadata and may be created only after the secret is genuinely replaced.

## Reason

WP-SYNC-11A was correctly validated for the July 31 three-position state but its static funded flags and date-bound Alpha Vantage evidence did not automatically remain valid after L0CK became a funded position or for later report dates. A live August 5 audit proved that the architecture itself remained sound while provider redundancy was not operational.

Keeping separate production pricing implementations created unnecessary divergence: the canonical routine used WP11A while PR #78's fresh-package path still inherited the older current-session route. Converging both paths restores determinism and makes one pricing contract govern release qualification.

## Evidence

```text
initial_live_audit_run=31255211953
repaired_four_position_live_audit_run=31258172996
repaired_four_position_artifact=9022002190
fresh_package_WP11A_route_run=31258280491
fresh_package_diagnostics_artifact=9022036048
```

## Consequence

Future portfolio activation of another ETF automatically expands the funded pricing gate when the authoritative portfolio state changes, provided the exact trading line exists uniquely in the provider registry. No separate manual `funded: true` edit may be relied upon as the gate authority.

The current release remains blocked until a second provider produces valid same-date evidence for all four funded positions. The preferred next attempt is a rotated Alpha Vantage credential; if Alpha coverage is insufficient, Leeway, EODHD or Marketstack must be configured without weakening the gate.

## Authority boundary

This decision changes pricing-state authority and workflow routing only. It does not authorize portfolio mutation, real broker execution, report delivery, recipient changes or commercial redistribution of provider data.
