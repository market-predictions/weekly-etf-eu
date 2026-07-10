# Decision — ETF-EU-MVP20A Real Transport Layer Authority

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP20A_REAL_TRANSPORT_LAYER_DECISION_20260710`

## Decision

Implement an isolated EU-specific package transport runner for controlled resend:

```text
runtime/send_etf_eu_delivery_package.py
```

The runner uses explicit package inputs and does not infer inherited U.S. production report filenames, U.S. portfolio state, or U.S. recipient authority.

## Rationale

`send_report.py` and `send_report_OLD.py` remain tied to inherited `weekly_analysis*` report discovery and legacy recipient assumptions. For the EU controlled resend path, transport must be explicit and package-bound.

## Authority boundary

The transport runner may only send a package that has already passed:

```text
client_grade_package_ready=true
ready_for_controlled_resend=true
```

Transport evidence must preserve:

```text
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
receipt_confirmed=false unless separately verified
```

## Guard rule

Real send mode remains gated by:

```text
delivery_mode=send
send_confirmation=confirm_guarded_send
```

Push-triggered runs are forced to `validate_only` and cannot send.

## Evidence rule

Transport success may only mean SMTP transport returned without exception and must retain the caveat:

```text
not an end-recipient inbox receipt
```

A separate receipt check remains required before `receipt_confirmed=true` can ever be claimed.

## Operational effect

`ETF-EU-MVP20A_REAL_TRANSPORT_LAYER_IMPLEMENTATION` can close as:

```text
completed_real_transport_layer_implemented_not_executed
```

The next package is:

```text
ETF-EU-MVP20B_GUARDED_CONTROLLED_RESEND_EXECUTION
```
