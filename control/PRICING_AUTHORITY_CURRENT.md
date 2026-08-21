# Weekly ETF EU — Current Pricing Authority

Status: CURRENT
Effective from merged PR #112 / main commit `5cc712582f86a51951cf57c55992f0ddc49a6ff1` (2026-08-18).

## Purpose

This file is the canonical human-readable summary of current production close-price authority. Historical two-provider-consensus wording in older issues, work packages, reports, metadata notes or audit records is provenance only and MUST NOT be interpreted as current production policy.

## Current production rule

1. Establish source-independent UCITS trading-line identity from the canonical symbol registry using ISIN + exact trading line (ticker + exchange/MIC + currency).
2. A pricing provider may be used only when its configured provider symbol is statically bound to that canonical trading line and returned identity evidence does not contradict it.
3. One qualified, correctly bound provider returning the exact requested completed-session close is sufficient for valuation-grade pricing.
4. Such a line is `fresh_exact_unverified` when no usable independent exact same-date verifier is available.
5. A second correctly bound provider with an exact same-date price within tolerance upgrades the line to `fresh_exact_verified`.
6. The selected valuation price remains the primary provider close; verifier prices validate rather than replace or median-blend it.
7. A stale, missing or unbound verifier does not invalidate a correctly bound exact primary.
8. Two accepted exact same-date providers outside tolerance produce `provider_disagreement` and fail closed.
9. No exact requested-date close, broken canonical trading-line identity, broken primary provider-symbol binding, explicit returned-symbol mismatch, venue mismatch or currency mismatch remain fail-closed.

## Explicitly retired rule

The following rule is retired and MUST NOT be used for current production decisions:

`every funded line requires two live providers with same-date close consensus before valuation-grade pricing`

Compatibility fields or CLI names containing `consensus` may remain in code/artifacts, but after PR #112 they represent exact-close pricing authority compatibility semantics, not a universal requirement for two live sources.

## Authority boundaries

This pricing rule does not by itself create fundability, allocation, portfolio mutation, trade-ledger mutation, delivery authority, SMTP authority or broker execution authority.

## Source of truth hierarchy

For current behavior use, in order:

1. live merged pricing/runtime code on `main`;
2. exact current tests/contracts implementing PR #112 semantics;
3. this current pricing authority summary;
4. current `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`;
5. historical issues/work packages/metadata only as provenance.

Relevant implementation files include:
- `pricing/ucits_provider_identity_binding.py`
- `pricing/ucits_price_qualification_policy.py`
- `pricing/ucits_primary_verification_legacy.py`
- `pricing/build_ucits_close_price_validation_basket_results.py`
- `pricing/ucits_close_price_validation_contract_v2.py`
- `runtime/build_etf_eu_client_grade_report_state_v2.py`
- `tools/build_etf_eu_routine_report_package.py`
- `tools/build_etf_eu_routine_report_package_v2.py`

## Incident that caused the change

The 2026-08-17 run demonstrated the liveness defect: Alpha Vantage had exact 2026-08-17 closes for all six funded lines while Yahoo remained on 2026-08-14. The retired two-live-source gate blocked all six despite valid exact primary closes. PR #112 separated exact primary close authority from independent verification and was independently assured before merge.
