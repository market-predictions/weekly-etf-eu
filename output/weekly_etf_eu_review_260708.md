# Weekly ETF EU Review | English Companion | 2026-07-08

> **Status:** cash-only bootstrap. This is not a production publication and no email delivery was performed.

## 1. Status

The EU/UCITS version of the Weekly ETF Review is in bootstrap mode.

- **Current state:** cash-only bootstrap.
- **Funded UCITS holdings:** none.
- **U.S. ETFs:** research proxies only, not investable portfolio instruments in this EU model.
- **UCITS candidates:** require ISIN, KID/PRIIPs and trading-line verification.
- **Pricing preflight:** non-authoritative connectivity test, no valuation authority.
- **Production delivery:** disabled.

## 2. Current portfolio state

| Component | Value |
|---|---:|
| Starting capital | EUR 100000.00 |
| Cash | EUR 100000.00 |
| Invested market value | EUR 0.00 |
| Total portfolio value | EUR 100000.00 |
| Funded positions | 0 |

No UCITS ETFs are funded yet. The portfolio remains fully in cash until instruments pass the EU investability contract.

## 3. Investability gate

An ETF can become fundable only after at least the following fields are verified:

| Requirement | Status |
|---|---|
| ISIN | required |
| UCITS status | required |
| PRIIPs/KID availability | required |
| Exchange and ticker | required |
| Trading currency | required |
| Pricing line | required |
| Product cost / TER | to be added where available |
| Replication method | to be added where available |
| Accumulating / distributing | to be added where available |

## 4. Research proxies

U.S. ETFs may be used only as research proxies or benchmark references. They must not appear as funded EU portfolio holdings.

| Theme | U.S. proxy | EU role | Status |
|---|---|---|---|
| S&P 500 core beta | SPY — research proxy only | Core U.S. equity exposure through UCITS ETF | UCITS candidate verification required |
| Semiconductor leadership | SMH — research proxy only | Semiconductor thematic exposure through UCITS ETF | UCITS candidate verification required |
| Gold / hard-asset hedge | GLD — research proxy only | Gold or commodity hedge through EU-listed product | UCITS candidate verification required |
| Infrastructure / real asset capex | PAVE — research proxy only | Infrastructure exposure through UCITS ETF | UCITS candidate verification required |

## 5. UCITS candidate registry

The table below shows registry candidates and optional pricing preflight status. This table is **not a portfolio**, **not a buy recommendation** and **not valuation authority**.

| Role | Instrument | ISIN | Trading line | Status | U.S. proxy | Pricing preflight | Portfolio status |
|---|---|---|---|---|---|---|---|
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | verified_candidate_not_funded | SPY — research proxy only | non-authoritative price observed CSPX.L: 800.12 on 2026-07-08; non-authoritative price observed SXR8.DE: 702.24 on 2026-07-08 | not funded; no valuation authority |
| Semiconductor thematic exposure | VanEck Semiconductor UCITS ETF | IE00BMC38736 | SMH / USD / primary_line_pending_verification | candidate_requires_verification | SMH — research proxy only | not tested / not applicable | not funded; no valuation authority |
| Gold / hard-asset hedge | iShares Physical Gold ETC | TBD | SGLN / pending_verification / pending_verification | policy_review_required_not_ucits | GLD — research proxy only | not tested / not applicable | not funded; no valuation authority |
| Infrastructure / real-asset capex exposure | iShares Global Infrastructure UCITS ETF | TBD | INFR / pending_verification / pending_verification | candidate_requires_verification | PAVE — research proxy only | not tested / not applicable | not funded; no valuation authority |

## 6. UCITS registry status

The UCITS registry now contains bootstrap candidates, but there is no funded model portfolio yet. Candidates remain unfunded until ISIN, KID/PRIIPs, trading line, currency, pricing quality, liquidity and portfolio role are sufficiently checked.

## 7. Next build steps

1. Enrich the UCITS symbol registry with additional verified ISINs and trading lines.
2. Map research proxies to actual UCITS candidates.
3. Promote pricing from connectivity test to valuation-grade only after a separate pricing-lineage decision.
4. Only then build a funded model portfolio.
5. Keep production delivery disabled until all EU validations pass.

## Production report maturity

This layer makes the report suitable as a Dutch-first client review surface, but it does not change portfolio or delivery authority.

| Checkpoint | Current status |
|---|---|
| Report role | Dutch report is the primary client report |
| English version | companion/operator-facing version |
| Client decision | research and evidence phase; no buy recommendation |
| UCITS portfolio | no funded UCITS holdings |
| Portfolio impact | no portfolio mutation |
| Pricing quality | agreement-gate evidence visible, not valuation authority |
| Fundability | fundability gate status visible; no candidate is automatically fundable |
| Production delivery | no production delivery |
| Delivery evidence | no delivery receipt |

The client-facing report is Dutch-first. U.S. ETFs remain research proxies and must not be presented as investable EU portfolio positions.

## Agreement-gate pricing surface

The pricing rows below are candidate evidence rows. This section is **not a portfolio**, **not a buy recommendation** and **not valuation authority**.

| Instrument | ISIN | Trading line | Agreement-gate pricing | Portfolio status |
|---|---|---|---|---|
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | status=provisional; date=-; close=-; currency=-; sources=- | not funded; no valuation authority |
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 / EUR / Xetra | status=provisional; date=-; close=-; currency=-; sources=- | not funded; no valuation authority |

## Fundability gate status

The fundability gate status is visible as report evidence. This section does not promote any candidate to fundable and creates no funding authority.

- **Candidates:** 4.
- **Not fundable / blocked:** 4.
- **candidate_promotion=false**.
- **funding_authority=false**.
- **portfolio_mutation=false**.
- **production_delivery=false**.

| Instrument | ISIN | Fundability gate status | Gate blockers | Gates | Authority |
|---|---|---|---|---|---|
| iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | not_fundable_blocked | pricing_quality:pricing_evidence_provisional_or_reference_only, pricing_quality:valuation_grade_false, tradability_liquidity:liquidity_check_missing_or_not_passed, tradability_liquidity:spread_check_missing_or_not_passed, tradability_liquidity:broker_availability_not_confirmed, portfolio_role:portfolio_role_review_missing | decision=blocked; eu_investability=passed; instrument_identity=passed; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=passed | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
| VanEck Semiconductor UCITS ETF | IE00BMC38736 | not_fundable_blocked | eu_investability:ucits_status_not_fully_confirmed, eu_investability:domicile_missing_or_pending, eu_investability:distribution_policy_missing_or_pending, eu_investability:replication_method_missing_or_pending, trading_line:no_verified_trading_line, pricing_quality:agreement_gate_valuation_status_missing | decision=blocked; eu_investability=blocked; instrument_identity=passed; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=blocked | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
| iShares Physical Gold ETC | TBD | not_fundable_blocked | instrument_identity:isin_missing_or_placeholder, instrument_identity:instrument_type_not_ucits_etf_under_current_policy, eu_investability:ucits_status_not_fully_confirmed, eu_investability:priips_kid_not_confirmed_available, eu_investability:domicile_missing_or_pending, eu_investability:ter_pct_missing_or_pending | decision=blocked; eu_investability=blocked; instrument_identity=blocked; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=blocked | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
| iShares Global Infrastructure UCITS ETF | TBD | not_fundable_blocked | instrument_identity:isin_missing_or_placeholder, eu_investability:ucits_status_not_fully_confirmed, eu_investability:priips_kid_not_confirmed_available, eu_investability:domicile_missing_or_pending, eu_investability:distribution_policy_missing_or_pending, eu_investability:replication_method_missing_or_pending | decision=blocked; eu_investability=blocked; instrument_identity=blocked; portfolio_role=blocked; pricing_quality=blocked; tradability_liquidity=blocked; trading_line=blocked | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |

## 8. Delivery status

This output is a non-delivered bootstrap report only. No PDF rendering, portfolio execution or email delivery was performed.
