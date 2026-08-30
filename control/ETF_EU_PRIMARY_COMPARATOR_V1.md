# Weekly ETF EU — Primary Comparator Contract V1

**Status:** ACTIVE PRODUCT ACCOUNTABILITY POLICY  
**Effective:** 2026-08-30  
**Machine config:** `config/etf_eu_primary_comparator.yml`

## Decision

The primary Weekly ETF EU accountability comparator is the exact Xetra EUR trading line of **Vanguard FTSE All-World UCITS ETF USD Acc (VWCE)**:

- ISIN: `IE00BK5BQT80`
- MIC: `XETR`
- ticker: `VWCE`
- trading currency: `EUR`
- benchmark: FTSE All-World Index
- canonical identity source: `config/ucits_symbol_registry.yml`

## Why this comparator

VWCE is the simplest already-verified EU/UCITS broad global-equity alternative available inside the current identity/pricing boundary. It is investable in the intended product domain, uses an exact canonical European trading line, and avoids importing a U.S. proxy or adding a new unverified pricing identity merely to create a benchmark.

The model portfolio also holds cash and defensive/bond exposure. VWCE is therefore a **deliberately simple opportunity-cost comparator**, not a risk target, allocation target, or automatic trading signal. Active return must be read together with drawdown and cash contribution/rationale.

## Stable rules

1. Comparator identity and methodology are stable from the effective date.
2. Changing the primary comparator requires an explicit governed product-policy decision; underperformance is not a valid reason by itself.
3. Portfolio and comparator performance use compatible exact valuation dates where available.
4. Current production accountability may not silently interpolate a missing comparator close.
5. Historical missing data is explicit unresolved evidence until lawfully backfilled from exact-date evidence.
6. A U.S. proxy may support research context only; it may not silently replace the exact VWCE client-accountability line.
7. Comparator evidence never creates funding, allocation, broker, portfolio-mutation, pricing-source-promotion or delivery authority.

## Minimum client interpretation

The report should show:
- portfolio return and comparator return over the same supported periods;
- active return in percentage points;
- portfolio and comparator drawdown;
- cash contribution/drag when evidenced, otherwise explicit unavailable/unresolved state;
- top contributor and detractor;
- position contribution where evidenced.

No optimizer, Sharpe/Sortino layer, Brinson attribution or automated benchmark switching is required by this contract.

## Pricing authority

Comparator pricing follows `control/PRICING_AUTHORITY_CURRENT.md`: exact canonical trading-line identity first; a qualified correctly bound exact-date primary close may be valuation-grade without a current verifier; verifier agreement upgrades confidence; accepted same-date disagreement fails closed.
