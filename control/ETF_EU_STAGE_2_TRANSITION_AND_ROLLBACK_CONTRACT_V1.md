# ETF EU Stage-2 Transition and Rollback Contract V1

**Status:** shadow-only cutover-readiness control  
**Destination priority:** developed markets outside the United States  
**Initial implementation candidate:** IXUA, ISIN `IE000R4ZNTN3`, Xetra EUR line  
**Activation authority:** none

## 1. Purpose

Stage 2 is not a generic continuation of Stage 1. It is a controlled attempt to close the largest remaining strategic gap while reducing existing U.S. large-cap overlap and preserving an explicit liquidity reserve.

The initial Stage-2 destination is the developed-ex-U.S. equity sleeve because:

- it is the largest unresolved donor target;
- an exact UCITS candidate has been identified;
- VWCE is not an exact developed-ex-U.S. implementation;
- SXR8 is the first incumbent identified for overlap reduction.

## 2. Entry gates

A Stage-2 readiness artifact may become `ready_for_separate_activation_review` only when all gates pass:

1. donor contract pin is valid and immutable;
2. Stage 1 has been separately authorized, applied to official model state and receipt-confirmed;
3. the exact post-Stage-1 portfolio state is available;
4. the intended IXUA line has identity, document, valuation and tradability grades of `pass`;
5. the IXUA evidence has not expired;
6. the donor still assigns an add direction to developed-ex-U.S. equity;
7. the destination remains within position and concentration caps;
8. the EUNA risk-budget review is valid;
9. no pricing, spread, KID, venue or authority blocker remains;
10. a separate activation authorization is supplied.

A shadow allocator or old connectivity close does not satisfy these gates.

## 3. Stage-2 sizing policy

Stage 2 may add only one new destination in a run.

Default limits:

```text
protected_cash_floor_pct_nav = 25.00
maximum_stage_2_gross_turnover_pct_nav = 15.00
maximum_stage_2_destination_weight_pct_nav = 15.00
maximum_sxr8_reduction_pct_nav_per_run = 5.00
minimum_trade_size_pct_nav = 2.00
maximum_total_positions = 8
```

The Stage-2 target is the lesser of:

- the unresolved donor target;
- the maximum Stage-2 destination weight;
- the Stage-2 turnover budget;
- the amount fundable under the governed source order.

Whole-share rounding and estimated transaction costs must be applied after the weight budget is determined.

## 4. Funding-source order

### Source 1 — excess cash

Use only cash above the protected cash floor. Cash at or below the floor is unavailable.

### Source 2 — SXR8 overlap reduction

If excess cash is insufficient and the destination evidence is complete, Stage 2 may source the remaining amount from SXR8 up to the per-run reduction cap.

SXR8 may be reduced only when:

- VWCE remains funded as global core;
- the developed-ex-U.S. destination is exact and activation-ready;
- the overlap review still identifies SXR8 as the first reduction candidate;
- the resulting SXR8 weight is non-negative;
- total turnover remains within budget.

### Source 3 — EUNA

EUNA is third priority and unavailable by default.

EUNA may fund Stage 2 only if a new accepted risk-budget artifact states that at least one of these is true:

- its weight exceeds the governed maximum role weight;
- the defensive reserve exceeds a later policy cap;
- its low-volatility-diversifier classification fails.

There is no automatic EUNA sale.

## 5. Blocking behavior

If any entry gate fails, the Stage-2 artifact must:

- set readiness to `blocked`;
- list every blocker;
- produce no executable trade intents;
- preserve source-order calculations only as non-authoritative capacity analysis;
- retain all portfolio, funding, execution and delivery authority flags as false.

## 6. Rollback

Rollback is state-oriented, not transaction-oriented.

A cutover package must preserve:

1. the last accepted official portfolio state before Stage 1;
2. the accepted official state after Stage 1, if Stage 1 was activated;
3. immutable donor and EU commit references;
4. accepted pricing and product-evidence artifacts;
5. exact ledger and delivery evidence for any separately authorized mutation.

A rollback decision may select the last accepted official state as the new target for a separately authorized package. It must not automatically generate reverse orders, infer trades from report text or rewrite the ledger.

## 7. Authority boundary

This contract:

- does not activate Stage 1 or Stage 2;
- does not recommend or execute a transaction;
- does not mutate official portfolio state;
- does not write a trade ledger;
- does not authorize funding, execution or production delivery.

A separate activation package must reproduce the readiness artifact from fresh evidence and contain explicit authorization.