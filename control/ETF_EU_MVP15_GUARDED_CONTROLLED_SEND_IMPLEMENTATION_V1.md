# ETF EU MVP15 guarded controlled-send implementation v1

## Purpose

MVP15 implements the static guarded path for a later controlled EU workflow operation.

## Scope

MVP15 implements workflow guard structure, confirmation input, evidence helper support, receipt check helper support and static validators. It does not execute outbound delivery during closeout.

## Source evidence

```text
source_work_package=ETF-EU-MVP14
mvp14_plan_status=guarded_plan_ready
mvp14_selected_next_package=ETF-EU-MVP15
reference_run_id=28963021481
reference_conclusion=success
reference_mode=dry_run
```

## Reference architecture rule

```text
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
```

## Decision framework

```text
guarded_send_implementation_static_green
guarded_send_implementation_hardening_required
```

## Input/state contract

MVP15 consumes MVP14 through MVP09 validation evidence and the EU workflow.

## Output contract

MVP15 emits a static implementation artifact, notes, validator, tests and decision record.

## Operational runbook

Run MVP15 validator/tests plus MVP14 through MVP09 regressions.

## Workflow implementation

MVP15 preserves validate_only, dry_run and send choices, adds `send_confirmation`, keeps push-triggered runs in validate_only, and isolates the guarded placeholder path behind mode and confirmation.

## Confirmation gate

The guarded path requires both `delivery_mode=send` and `send_confirmation=confirm_guarded_send`.

## Pre-transport evidence

The workflow contains a pre-step evidence helper call for the guarded path.

## Transport result evidence

The workflow contains a post-step evidence helper call and a static placeholder. MVP15 closeout does not perform outbound transport.

## Receipt semantics

Transport-layer evidence is not an end-recipient receipt. A receipt claim requires a separate check artifact.

## Delayed verification

The workflow contains a delayed receipt-check helper call with a ten-minute configuration.

## Rollback rule

Rollback target is the previous guarded behavior if validation or evidence fails.

## Donor-port comparison

MVP15 preserves donor-port comparison and records no U.S. assumptions copied.

## Secret and recipient handling

Private runtime values and plaintext recipient values must not be recorded.

## Success-claim rule

MVP15 closeout records no delivery success claim.

## Failure handling

If validation fails, select ETF-EU-MVP15-FIX.

## What this package may create

Workflow update, helper update, receipt helper, contract, artifact, notes, validator, tests, decision record and control-doc updates.

## What this package must not execute

MVP15 must not execute outbound transport or mutate portfolio state.

## Next package

```text
ETF-EU-MVP16
```

## Validation requirements

Validate confirmation gate, workflow isolation, evidence helpers, receipt helper, boundary facts, donor reference fields and selected next package.
