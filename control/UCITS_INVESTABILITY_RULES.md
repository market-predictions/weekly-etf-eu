# UCITS Investability Rules

## Purpose

These rules define when an ETF may be treated as investable in the Weekly ETF EU Review and its broker-neutral model portfolio.

## Hard requirements for funded model holdings

A funded model holding must have:

- ISIN;
- exact share-class identity;
- UCITS status confirmed;
- PRIIPs / KID availability confirmed for the intended Dutch/EU retail product context;
- verified exchange ticker and venue;
- trading currency;
- usable completed-close pricing line;
- fund name;
- provider;
- investability status.

A pending verification status may be displayed in research or candidate surfaces, but it does not authorize model funding.

## Blocking statuses

A candidate is not fundable in the model if:

- it is U.S.-listed only;
- it lacks UCITS status;
- it lacks PRIIPs/KID availability for Dutch/EU retail clients;
- it has no verified exact exchange line;
- it has no usable completed-close pricing line;
- canonical ISIN, share class, venue, ticker or currency identity is unresolved;
- a concentration, currency or product-policy gate fails;
- it is only a research proxy.

## Broker-neutrality rule

Broker-specific account permission is not a model-investability requirement.

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

The Weekly ETF EU Review may classify a verified UCITS line as model-investable without naming or depending on a particular broker. It must disclose that actual availability, costs, order types, routing and account eligibility can differ by broker and account.

Broker contract IDs, local symbols and routing aliases are execution-layer mappings only. They must not replace the canonical identity:

```text
ISIN
+ exact share class
+ venue
+ exchange trading line
+ trading currency
```

A broker permission failure may block a real order through that account, but it must not retroactively invalidate the broker-neutral model allocation.

## Preferred characteristics

Preferred candidates have:

- EUR trading line where practical;
- sufficient liquidity;
- acceptable spreads;
- low TER / ongoing charges;
- clear replication method;
- accumulating share class where tax/reporting preference is neutral or user has not specified otherwise;
- transparent benchmark index;
- acceptable tracking quality.

## Report disclosure

The report should disclose, where available:

- ISIN;
- exchange ticker and venue;
- trading currency;
- UCITS status;
- KID status;
- TER;
- distribution policy;
- replication method;
- domicile;
- whether a U.S. ETF shown in the row is a research proxy only;
- that broker/account availability and transaction conditions may differ.

The report must not claim universal broker availability unless separately evidenced for the stated broker and account context.

## No personal tax advice

The report may mention tax-relevant product features such as domicile and distribution policy, but it must not provide personal tax advice.
