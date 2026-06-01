# Yahoo Verified-Fallback Contract V1

## Purpose

This contract defines the only safe path by which Yahoo/yfinance UCITS ETF closes may move from connectivity diagnostics toward a verified fallback source.

Yahoo/yfinance is not primary authority. It may only be considered as a fallback evidence source after explicit gates pass and the workflow records repo-native evidence.

## Layer 1 — decision framework

Yahoo fallback evidence may support portfolio valuation only when the portfolio decision already rests on a registry-approved UCITS ETF trading line. Yahoo evidence may never promote a candidate to fundable status by itself.

## Layer 2 — input/state contract

A Yahoo row is eligible for verified-fallback evaluation only when all of these gates are present in a machine-readable artifact:

1. `yahoo_symbol_registry_approved_for_diagnostics=true` — the Yahoo symbol is explicitly listed for the registry trading line.
2. `verified_fallback_policy_enabled=true` — the source policy explicitly allows Yahoo as a verified fallback, not just connectivity preflight.
3. `currency_matches_registry=true` — Yahoo currency equals the registry trading currency.
4. `fresh_close_present=true` — Yahoo returns a positive close and close date within the configured staleness limit.
5. `completed_session_validated=true` — the close date is proven to be a completed regular session for the venue.
6. `cross_source_check_passed=true` — the Yahoo close is within tolerance versus an independent source for the same ISIN/trading line/date/currency.
7. `lineage_recorded=true` — the artifact records symbol, source, date, currency, close, registry id, provider symbol and diagnostics.
8. `valuation_authority_blocked=true` — evaluation remains non-mutating until the valuation-pricing contract is separately revised.

If any gate fails, `eligible_for_verified_fallback=false`.

## Layer 3 — output contract

Yahoo fallback evaluations must not appear in client-facing reports as valuation-grade closes unless a later valuation-grade artifact explicitly accepts them under the UCITS valuation-pricing contract.

Diagnostic reports may state that Yahoo has a recent observed close, but must also state whether the mapping is ambiguous and whether fallback gates passed.

## Layer 4 — operational runbook

The workflow must:

1. build `output/pricing/yahoo_ucits_close_diagnostics_*.json`;
2. build `output/pricing/yahoo_verified_fallback_evaluation_*.json`;
3. validate that no Yahoo fallback artifact creates funding authority, portfolio mutation, PDF generation, email delivery or delivery receipt;
4. include the evaluation artifact in shadow validation evidence;
5. keep `valuation_authority=false` until a separate policy change and validation stack revision are made.

## Current authority rule

As of this contract version, Yahoo/yfinance remains non-authoritative connectivity only. The verified-fallback evaluation layer may prove useful prices exist, but it does not by itself create valuation authority.
