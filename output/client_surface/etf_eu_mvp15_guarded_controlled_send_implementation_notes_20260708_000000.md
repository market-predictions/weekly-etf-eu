# ETF-EU-MVP15 guarded controlled-send implementation

## Scope

MVP15 implements the guarded path statically after MVP14. It updates workflow structure and supporting helpers, but does not execute the guarded operation during closeout.

## Source evidence

```text
source_work_package=ETF-EU-MVP14
reference_run_id=28963021481
reference_conclusion=success
reference_mode=dry_run
```

## Weekly ETF donor architecture reference

MVP15 used `market-predictions/weekly-etf` as reference architecture only.

`weekly-etf-eu` remained the EU/UCITS source-of-truth.

```text
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

## Decision framework

```text
implementation_status=guarded_static_implementation_green
selected_next_package=ETF-EU-MVP16
```

## Input/state contract

MVP15 uses MVP14 through MVP09 evidence and EU workflow checks.

## Output contract

MVP15 emits workflow update, helper update, receipt helper, artifact, notes, validator, tests and decision record.

## Operational runbook

Run MVP15 validator/tests and MVP14 through MVP09 regression validators.

## Workflow implementation

The workflow preserves validate_only, dry_run and send choices, adds `send_confirmation`, and keeps push-triggered runs in validate_only.

## Confirmation gate

The guarded path requires `send_confirmation=confirm_guarded_send`.

## Evidence contract

The workflow contains pre-step and post-step evidence helper calls behind the guarded path.

## Receipt semantics

A transport-layer result is not an end-recipient receipt. Completion requires receipt confirmation.

## Delayed verification

A ten-minute delayed check helper is available as an artifact-producing step.

## Rollback rule

Rollback target is the prior guarded behavior if evidence or validation fails.

## Donor-port comparison

MVP15 preserves donor-port comparison and records no U.S. assumptions copied.

## Boundary rules

```text
guarded_operation_performed=false
guarded_mode_run_performed=false
completion_claimed=false
receipt_confirmed=false
private_values_exposed=false
plain_contact_values_exposed=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
```

## Failure handling

Use ETF-EU-MVP15-FIX if static validation fails.

## Decision

MVP15 selected ETF-EU-MVP16 because static guarded implementation is green and no guarded operation was performed in MVP15.

## Next package

```text
ETF-EU-MVP16
```
