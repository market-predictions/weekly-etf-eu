# Weekly ETF EU Review | English Companion | 2026-06-01

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
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | verified_candidate_not_funded | SPY — research proxy only | non-authoritative price observed CSPX.L: 817.70 on 2026-06-01; non-authoritative price observed SXR8.DE: 701.92 on 2026-06-01 | not funded; no valuation authority |
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

## 8. Delivery status

This output is a non-delivered bootstrap report only. No PDF rendering, portfolio execution or email delivery was performed.
