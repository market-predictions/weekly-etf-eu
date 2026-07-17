# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
MANUAL_DISPATCH_ACCEPTED_PACKAGE_20260717_141500
```

## Accepted package

```text
run_id=20260717_141500
report_date=2026-07-17
report_suffix=260717_06
source_workflow_run_id=29575699421
machine_validation_passed=true
visual_review_passed=true
readiness_gate_passed=true
ready_for_controlled_delivery=true
```

The accepted package is authoritative. Do not regenerate pricing, state, HTML or PDF before delivery.

## Active model state

```text
position_count=3
cash_eur=60439.44
invested_market_value_eur=39577.16
nav_eur=100016.60
real_broker_execution=false
portfolio_mutation=false
```

| Ticker | Role | Shares | Value | Weight | Current action |
|---|---|---:|---:|---:|---|
| VWCE | Global core | 151 | €24,963.32 | 24.959177% | Hold after first tranche |
| EUNA | Aggregate-bond stabiliser | 1,526 | €7,497.24 | 7.495996% | Hold after first tranche |
| SXR8 | U.S. equity overweight | 10 | €7,116.60 | 7.115419% | Hold; no second tranche |

No automatic add, reduce, exit, later tranche or satellite activation is authorised.

## Exact manual dispatch

In GitHub Actions, open:

```text
Weekly ETF EU current-package delivery workflow
```

Run from branch:

```text
main
```

Use these inputs exactly:

```text
delivery_mode=send
queue_path=control/prepared_delivery/etf_eu_current_package_delivery_request_20260717_141500.md
send_confirmation=confirm_guarded_send
```

Do not run the routine-production workflow. Do not re-run an older current-package job.

## Delivery safeguards already prepared

```text
accepted_package_lock=output/delivery_control/etf_eu_accepted_package_lock_20260717_141500.json
delivery_prep=output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260717_141500.json
authorization=output/delivery_authorization/etf_eu_guarded_send_authorization_20260717_141500.json
decision=output/delivery_control/etf_eu_controlled_delivery_decision_20260717_141500.json
transport_selection=output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260717_141500.json
prepared_queue=control/prepared_delivery/etf_eu_current_package_delivery_request_20260717_141500.md
```

The queue validator must confirm:

```text
four exact client files present
Git blob identities unchanged
machine_validation_passed=true
visual_review_passed=true
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

## Required transport verification

After dispatch:

1. inspect the workflow job and failing step, if any;
2. verify a new current-package transport result was committed;
3. require `transport_attempted=true`;
4. require `transport_success=true`;
5. require `send_executed=true`;
6. require a redacted message-reference hash;
7. keep `receipt_confirmed=false` until independent mailbox evidence exists.

The workflow has an idempotency gate. A prior successful result for the same queue and suffix blocks a second send.

## Delayed receipt verification

Approximately ten minutes after successful transport:

1. search the connected receipt mailbox for the 17 July 2026 Weekly ETF EU report;
2. match the recipient-safe report identity and transport timestamp;
3. confirm these four attachments:
   - Dutch PDF;
   - English PDF;
   - Dutch HTML;
   - English HTML;
4. reconcile attachment hashes against transport evidence;
5. store only redacted receipt metadata and booleans;
6. do not resend when the existing message is found.

Only then may the closeout state:

```text
receipt_confirmed=true
production_delivery_cycle_closed=true
```

## Closeout files

After confirmed receipt, update:

```text
output/run_manifests/etf_eu_routine_run_manifest_2026-07-17_20260717_141500.json
output/run_manifests/etf_eu_production_delivery_closeout_manifest_<runtime_run_id>.json
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DECISION_LOG.md
```

## Failure routing

```text
immutable lock mismatch -> stop; investigate changed output bytes
queue or authorization mismatch -> repair control artifacts; do not send
transport failure -> preserve redacted result and exact error; do not claim delivery
transport success without mailbox receipt -> wait and recheck; do not resend
mailbox receipt mismatch -> investigate attachments and message identity
valid transport plus confirmed receipt -> close production delivery cycle
```

## Later portfolio monitoring

Once delivery is closed, resume routine monitoring of:

1. VWCE role validity and broad-equity contribution;
2. EUNA stabilising contribution;
3. SXR8 overweight validity and overlap with VWCE;
4. remaining cash capacity;
5. separately authorised later tranches or satellite candidates.
