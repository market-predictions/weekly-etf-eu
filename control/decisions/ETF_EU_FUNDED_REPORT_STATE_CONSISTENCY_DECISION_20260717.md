# ETF EU Funded Report State Consistency Decision

Date: 2026-07-17  
Repository: `market-predictions/weekly-etf-eu`

## Decision

A technically successful render and machine-validation run is not acceptable when client-facing narrative contradicts the authoritative funded portfolio state.

For every funded-aware Weekly ETF EU report, all client surfaces must be derived from and reconciled to the complete current portfolio position set. A partial or singular funded overlay may not replace a multi-position state.

## Trigger

Preview run `20260716_214500` completed successfully and passed the existing client-grade v2 machine gate, but review found that:

- the authoritative portfolio contained funded VWCE, EUNA and SXR8 positions;
- the cockpit and conclusion described only one active model position;
- the allocation map and opportunity radar described funded VWCE and EUNA lanes as not funded or still awaiting closed verification gates;
- broker-availability language remained in model-investability copy;
- stale next-run instructions survived into the report;
- the position table omitted the pricing date.

The preview was rejected and superseded.

## Four-layer rule

### 1. Decision framework

A funded holding is reviewed as an incumbent position. It is not a candidate awaiting initial funding. Each incumbent must receive a current role, contribution, overlap, invalidation and action assessment.

No automatic add, reduction, exit, later tranche or satellite activation is authorised.

### 2. Input/state contract

The authoritative funded position set is:

```text
output/etf_eu_portfolio_state.json
```

The report builder and renderer must consume the full position set. Canonical identity remains:

```text
ISIN + exact share class + venue + exchange line + trading currency
```

A ticker-only or first-position-only overlay is insufficient.

### 3. Output contract

When the portfolio has funded positions, the Dutch and English reports must consistently expose:

- exact funded-position count;
- every funded ticker and ISIN;
- whole-share quantity;
- current model price and pricing date;
- market value, weight and phase target;
- model-only and no-real-order disclosure;
- active funded status in opportunity and allocation surfaces;
- cash and NAV reconciliation;
- portfolio contribution and overlap where available.

The report must not simultaneously describe a funded holding as:

```text
not funded
awaiting initial line verification
awaiting initial identity repair
blocked pending broker availability
```

### 4. Operational runbook

```text
portfolio state
→ normalized report state
→ funded-state reconciliation
→ renderer
→ strict funded-state consistency gate
→ complete visual/content review
→ preview closeout
```

A green machine gate is evidence of machine-contract compliance only. Visual and semantic acceptance remain separate requirements.

## Broker-neutral authority

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

Broker availability, contract identifiers, routing and account permissions may not appear as model-investability gates. They belong only to an optional real-execution adapter.

## Validator rule

The strict report validator must fail when:

- funded-position count and report summary disagree;
- a funded ticker is absent from the client report;
- a lane containing a funded ticker is not marked active;
- funded lanes contain broker-dependent model gates;
- singular first-position wording is used for a multi-position portfolio;
- stale VWCE or EUNA pre-activation wording survives;
- funded consistency metadata is absent or inconsistent.

## Historical evidence rule

Rejected preview run `20260716_214500` remains immutable historical evidence. It is marked as superseded and may not be delivered, promoted or reused as current report authority.

## Implementation

```text
runtime/render_etf_eu_client_grade_v2_funded.py
tools/validate_etf_eu_client_grade_report_v2_standalone.py
tests/test_etf_eu_cap01.py
```

Corrected preview identity:

```text
run_id=20260717_005500
report_suffix=260717
execution_mode=generate_validate_only
production_delivery_authority=false
```

## Authority exclusions

This decision does not authorise:

```text
portfolio mutation
real broker execution
email delivery
production delivery
valuation-grade promotion
automatic allocation change
```
