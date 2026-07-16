# ETF EU Broker-Neutral Model Investability Decision

Date: 2026-07-16  
Repository: `market-predictions/weekly-etf-eu`  
Status: accepted and implemented

## Current issue

The routine allocation review `20260716_092600` treated broker-account product permission for VWCE and broker execution-symbol confirmation for the aggregate-bond line as prerequisites for model funding.

That made the general Weekly ETF EU Report and its repository model portfolio dependent on a particular broker/account context, even though the system explicitly operates as:

```text
model_portfolio_only=true
real_broker_execution=false
```

## Root cause

Two different authority questions were combined:

1. whether a UCITS ETF and exact exchange trading line meet the broker-neutral product, identity, pricing and portfolio-policy gates for inclusion in the repository model;
2. whether a specific broker account can execute a real order in that contract.

The first belongs to the decision framework and input/state contract. The second belongs to an optional real-execution adapter.

## Decision

The Weekly ETF EU Report and its model portfolio are broker-neutral.

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

A missing broker permission, broker contract ID or broker routing alias must not block a model allocation when the canonical UCITS identity, exact exchange line, fresh completed-close pricing and all portfolio-policy gates pass.

Broker-specific checks are required only before a real order is prepared or submitted through that broker/account.

## Decision framework

Model investability requires:

```text
verified UCITS product
+ PRIIPs/KID availability
+ canonical ISIN and exact share class
+ verified exchange venue and trading line
+ trading currency
+ usable completed-close price
+ liquidity/concentration/product-policy gates
+ whole-share sizing
+ cash-policy reconciliation
```

It does not require a named broker.

## Input/state contract

Canonical identity is:

```text
ISIN
+ exact share class
+ venue
+ exchange trading line
+ trading currency
```

Issuer, market-data-vendor and broker identifiers are typed aliases. They may support lookup, but they do not replace canonical identity.

For `IE00BDBRDM35`, the model registry must reconcile the Xetra exchange line independently of any broker implementation while preserving known aliases such as `AGGH`, `EUNA`, and `EUNA.DE` in their correct roles.

## Output contract

The report may state that an instrument is model-investable or funded in the broker-neutral model when the model gates pass.

The report must also disclose:

> Actual availability, transaction costs, order types, routing and account eligibility can differ by broker and account.

The report must not claim universal availability through every broker.

## Operational runbook

Broker-neutral model path:

```text
fresh exact-line pricing
→ allocation decision
→ allocation validation
→ explicit model-capital authority
→ model portfolio and ledger mutation
→ report generation
```

Optional real-execution path:

```text
canonical model trade intent
→ selected broker adapter
→ contract lookup
→ account permission and eligibility check
→ order preview
→ explicit real-order authority
```

A failure in the optional real-execution path blocks only that real order. It does not retroactively invalidate the model decision.

## Historical evidence rule

Historical run artifacts are immutable evidence and are not rewritten. The broker-specific blocker wording in the `20260716_092600` review remains part of that historical run.

This decision and the updated live controls supersede that wording prospectively.

## Implementation

Updated:

```text
runtime/build_etf_eu_allocation_decision.py
tools/validate_etf_eu_allocation_decision.py
tests/test_etf_eu_cap01.py
control/ETF_EU_CAPITAL_ACTIVATION_POLICY_V1.md
control/UCITS_INVESTABILITY_RULES.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

## Portfolio and delivery boundary

```text
portfolio_mutation=false
trade_ledger_mutation=false
real_broker_order=false
email_send=false
production_delivery=false
historical_artifact_rewrite=false
```

The current portfolio remains 10 SXR8 shares and EUR 92,900 cash until a new run obtains fresh exact-line pricing and issues a separate allocation decision.
