# ETF EU MVP06 sender entrypoint implementation or validation v1

## Purpose

Implement and validate an EU-specific sender preflight entrypoint that selects canonical ETF EU reports without sending.

## Scope

MVP06 creates `runtime/send_etf_eu_report_runtime_html.py` and validates its no-send preflight behavior. MVP06 does not run delivery_mode=send and does not remove the workflow send guard.

## Source evidence

MVP06 starts from MVP05. validate_only and dry_run are green. Delivery manifest and run bundle validation passed for run `20260708_142840`.

## Sender entrypoint implemented

```text
eu_sender_entrypoint_path=runtime/send_etf_eu_report_runtime_html.py
eu_sender_entrypoint_created=true
eu_sender_entrypoint_selected=true
```

## Sender preflight behavior

The sender entrypoint supports a callable no-send preflight function:

```text
validate_etf_eu_sender_preflight(output_dir, report_suffix=None, delivery_mode=preflight_no_send)
```

## Dutch-primary and English companion support

The entrypoint selects:

```text
Dutch primary: output/weekly_etf_eu_review_nl_<YYMMDD>.md
English companion: output/weekly_etf_eu_review_<YYMMDD>.md
```

## Non-canonical artifact handling

The entrypoint ignores non-canonical ETF EU draft artifacts such as `*_draft.md` and `*_mature_draft.md`.

## U.S. report-name rejection

The entrypoint does not select inherited `weekly_analysis*` report names.

## Send guard decision

The workflow send guard remains present.

```text
workflow_send_guard_present=true
workflow_send_guard_removed=false
delivery_mode_send_unlocked=false
send_enablement_allowed=false
```

## Boundaries preserved

```text
send_performed=false
production_delivery=false
email_delivery=false
delivery_receipt=false
delivery_success_claimed=false
delivery_success_claim_allowed=false
```

## Next package

```text
ETF-EU-MVP07 — ETF EU manifest transition and controlled-send preflight
```

## Validation requirements

The MVP06 validator must confirm the EU sender entrypoint exists, validates canonical Dutch-primary and English companion selection, ignores non-canonical artifacts, does not select inherited report names, performs no send, preserves the workflow send guard, and selects ETF-EU-MVP07.
