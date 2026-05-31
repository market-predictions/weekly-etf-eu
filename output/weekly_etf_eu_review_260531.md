# Weekly ETF EU Review | English Companion | 2026-05-31

> **Status:** cash-only bootstrap. This is not a production publication and no email delivery was performed.

## 1. Status

The EU/UCITS version of the Weekly ETF Review is in bootstrap mode.

- **Current state:** cash-only bootstrap.
- **Funded UCITS holdings:** none.
- **U.S. ETFs:** research proxies only, not investable portfolio instruments in this EU model.
- **UCITS candidates:** require ISIN, KID/PRIIPs and trading-line verification.
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

## 5. UCITS registry status

The UCITS registry is not yet populated with verified instruments. Candidates remain `candidate_requires_verification` until ISIN, KID/PRIIPs, trading line, currency and pricing are checked.

## 6. Next build steps

1. Populate the UCITS symbol registry with verified ISINs and trading lines.
2. Map research proxies to actual UCITS candidates.
3. Add pricing for European trading lines and currencies.
4. Only then build a funded model portfolio.
5. Keep production delivery disabled until all EU validations pass.

## 7. Delivery status

This output is a non-delivered bootstrap report only. No PDF rendering, portfolio execution or email delivery was performed.
