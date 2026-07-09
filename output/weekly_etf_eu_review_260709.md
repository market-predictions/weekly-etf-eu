# Weekly ETF EU Review | English Companion | 2026-07-09

> **Package status:** EU/UCITS client package under validation. This report is not advice, not a portfolio instruction and not valuation authority.

## 1. Executive summary

The EU/UCITS version uses UCITS trading lines only as potentially investable instruments. U.S. ETF symbols do not belong in the primary client table and are retained only in the appendix as research references.

- **Model state:** cash-only, no funded UCITS positions.
- **Decision:** no allocation yet; complete data quality and trading-line verification first.
- **Price information:** non-authoritative connectivity or diagnostics only until separate valuation lineage is approved.

## 2. Portfolio overview

| Component | Value |
|---|---:|
| Starting capital | EUR 100000.00 |
| Cash | EUR 100000.00 |
| Invested market value | EUR 0.00 |
| Total portfolio value | EUR 100000.00 |
| Funded positions | 0 |

## 3. UCITS watchlist

This table shows only ISIN-first UCITS trading lines that are clean enough for the primary client watchlist. Unresolved or policy-review items are excluded from this main table.

| Role | UCITS ETF | ISIN | Trading line | Data status | Portfolio status |
|---|---|---|---|---|---|
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | CSPX / USD / London Stock Exchange | non-authoritative close: 800.12 (2026-07-08) | Not funded; no valuation or funding authority |
| Core U.S. equity exposure | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | SXR8 / EUR / Xetra | no usable close; diagnostics required | Not funded; no valuation or funding authority |

## 4. Price validation and data quality

Prices in this package are diagnostic. A positive close in the pipeline proves connectivity, but it does not create valuation authority or a funding decision.

## 5. Decision cockpit / next action

| Question | Answer |
|---|---|
| Is there a funded position? | No |
| Is this advice? | No |
| Is pricing valuation-grade? | No |
| Next step | Complete PDF package and UCITS close-fetch validation before controlled resend |

## 6. Appendix: research proxies and diagnostics

The research references below are not investable instruments in this EU model. They must not be read as portfolio instruments.

| Theme | Research reference | EU role | Status |
|---|---|---|---|
| S&P 500 core beta | SPY | Core U.S. equity exposure through UCITS ETF | Research reference only; not investable in the EU model |
| Semiconductor leadership | SMH | Semiconductor thematic exposure through UCITS ETF | Research reference only; not investable in the EU model |
| Gold / hard-asset hedge | GLD | Gold or commodity hedge through EU-listed product | Research reference only; not investable in the EU model |
| Infrastructure / real asset capex | PAVE | Infrastructure exposure through UCITS ETF | Research reference only; not investable in the EU model |

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
| No pricing rows | - | - | no agreement-gate evidence | not funded; no valuation authority |

## Fundability gate status

The fundability gate status is visible as report evidence. This section does not promote any candidate to fundable and creates no funding authority.

- **Candidates:** 0.
- **Not fundable / blocked:** 0.
- **candidate_promotion=false**.
- **funding_authority=false**.
- **portfolio_mutation=false**.
- **production_delivery=false**.

| Instrument | ISIN | Fundability gate status | Gate blockers | Gates | Authority |
|---|---|---|---|---|---|
| No fundability rows | - | unavailable | no artifact available | - | candidate_promotion=false; funding_authority=false; portfolio_mutation=false; production_delivery=false |
