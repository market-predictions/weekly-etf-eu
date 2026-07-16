# Weekly ETF EU Routine Allocation Review

Run id: `20260716_092600`  
Review date: `2026-07-16`  
Status: `review_complete_no_model_mutation`

## Portfolio result

| Component | Result |
|---|---:|
| Cash | €92,900.00 |
| Invested market value | €7,100.00 |
| NAV | €100,000.00 |
| Funded positions | 1 |
| New trade intents | 0 |

## SXR8 incumbent review

| Field | Result |
|---|---|
| ISIN | IE00B5BMR087 |
| Exact line | Xetra / SXR8 / EUR |
| Shares | 10 |
| Entry price | €710.00 |
| Review price | €710.00 |
| Price date | 2026-07-14 |
| Unrealized P&L | €0.00 / 0.00% |
| Portfolio contribution | €0.00 |
| Current weight | 7.10% |
| First-tranche target | 7.50% |
| Action | Hold |
| Second tranche | Not authorized |

The latest validated exact-line close was retained because no fresher completed Xetra close was obtained through the available connected data path. No substitute or inferred price was used.

## VWCE verification

VWCE is now verified at fund, KID and exact Xetra-line level:

```text
isin=IE00BK5BQT80
venue=Xetra
exchange_ticker=VWCE
bloomberg_ticker=VWCE GY
reuters_ric=VWCE.DE
trading_currency=EUR
```

Funding remains deferred until:

1. a fresh completed Xetra close is available;
2. the configured broker account confirms product permission for the exact contract;
3. a new run-scoped allocation decision authorizes the first tranche.

The overlap review recognizes that VWCE already contains material U.S. equity exposure. A 25% VWCE first tranche plus the current SXR8 sleeve would produce approximately 22.54% direct and embedded U.S. exposure under the latest issuer country weight used in the review. This is acceptable within the current design but must remain visible.

## Aggregate-bond identity repair

The canonical share class is:

```text
isin=IE00BDBRDM35
share_class=EUR Hedged Accumulating
issuer_exchange_ticker=AGGH
bloomberg_identifier=EUNA
reuters_ric=EUNA.DE
```

The previous LSE GBP Hedged Distributing mapping with the same ISIN was removed. Broker execution-symbol mapping and a fresh completed Xetra close remain required before any allocation.

## Allocation decision

```text
portfolio_action=hold_sxr8_and_retain_cash
trade_intents=[]
portfolio_mutation=false
second_tranche_authorized=false
new_position_authorized=false
```

## Authority boundary

This is a repository model review only. No real brokerage order was placed, no production delivery was authorized and no email was sent.

## Canonical evidence

```text
output/instrument_verification/etf_eu_instrument_verification_20260716_092600.json
output/runtime/etf_eu_routine_allocation_review_20260716_092600.json
output/quality/etf_eu_routine_allocation_review_validation_20260716_092600.json
control/decisions/ETF_EU_ROUTINE_POSITION_AND_IDENTIFIER_DECISION_20260716.md
```
