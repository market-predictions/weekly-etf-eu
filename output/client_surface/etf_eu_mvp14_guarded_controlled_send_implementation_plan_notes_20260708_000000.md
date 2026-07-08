# ETF-EU-MVP14 guarded controlled-send implementation plan

## Scope

MVP14 is a planning and contract package after MVP13. Current workflow behavior remains unchanged.

## Source evidence

```text
source_work_package=ETF-EU-MVP13
reference_run_id=28963021481
reference_conclusion=success
reference_mode=dry_run
```

## Weekly ETF donor architecture reference

MVP14 used `market-predictions/weekly-etf` as reference architecture only.

`weekly-etf-eu` remained the EU/UCITS source-of-truth for contracts, state, pricing policy, language requirements, artifacts and boundaries.

```text
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

## Decision framework

```text
plan_status=guarded_plan_ready
selected_next_package=ETF-EU-MVP15
```

## Input/state contract

MVP14 uses MVP13 through MVP09 evidence and EU workflow preflight checks.

## Output contract

MVP14 emits plan artifact, notes, validator, tests and decision record.

## Operational runbook

Run MVP14 validator/tests and the MVP13 through MVP09 regression validators.

## Workflow implementation plan

The later package must preserve manual activation, validation-first behavior, second confirmation, pre-step evidence, post-step evidence, run-bundle linkage and rollback.

## Evidence contract plan

The later package must use redacted recipient policy, workflow/job/run identity, report paths, language pair, status fields and receipt semantics.

## Receipt semantics plan

A transport result is not an end-recipient inbox receipt. Receipt confirmation requires a separate check artifact.

## Delayed verification plan

A delayed check after about 10 minutes is required by the later package.

## Rollback plan

Rollback must restore the existing guarded behavior if validation or evidence fails.

## Donor-port comparison

MVP14 preserves MVP13 donor-port comparison and adds a controlled implementation plan dimension.

## Boundary rules

```text
plan_only=true
workflow_behavior_changed=false
mail_transport_behavior_changed=false
client_completion_claimed=false
live_operation_performed=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
```

## Failure handling

Use ETF-EU-MVP14-FIX if validation fails.

## Decision

MVP14 selected ETF-EU-MVP15 because MVP13 preflight was green, donor-port comparison was valid, and the EU workflow preserved the guard/evidence chain.

## Next package

```text
ETF-EU-MVP15
```
