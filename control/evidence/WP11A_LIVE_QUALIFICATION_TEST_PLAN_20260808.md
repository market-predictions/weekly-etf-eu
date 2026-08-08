# WP11A Live Qualification Test Plan — 2026-08-08

Purpose: exercise the existing WP-SYNC-11A multi-provider close-price engine against report date 2026-08-05 without using the 2026-07-31 historical evidence cache and without mutating portfolio, ledger, report delivery, or production authority.

## Scope

- Existing provider engine only: Leeway, EODHD, Marketstack, Alpha Vantage, Yahoo Chart.
- Exact provider registry and code at the test-branch base.
- Live calls with repository-configured secrets where available.
- No historical provider cache.
- Report date: 2026-08-05.
- Four current governed portfolio tickers are evaluated explicitly: VWCE, EUNA, SXR8, L0CK, even if a stale registry funded flag says otherwise.

## Pass criteria

1. Deterministic WP11A regression suite passes.
2. Qualification artifact contains all provider lanes with secret redaction intact.
3. For each of VWCE, EUNA, SXR8, L0CK, at least two live providers produce an admissible close on the same selected close date within the existing 1.0% tolerance.
4. At least one agreeing provider per line satisfies the existing identity-anchor policy.
5. No provider cache contributes to the result.
6. No portfolio or ledger mutation and no delivery action occurs.

## Interpretation

- If all pass criteria hold, WP11A is operationally successful for the current four-position pricing problem, subject to production-path integration and independent release assurance.
- If deterministic tests pass but live-provider criteria fail, WP11A remains a valid software architecture but is not an operationally complete solution to the current pricing problem.
- If the current four-position state is not represented by the WP11A funded-line contract, that is a state-contract defect and WP11A cannot be considered complete for the current portfolio until repaired and revalidated.
