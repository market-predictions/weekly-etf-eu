# ETF-EU-MVP04-FIX weekly-etf delivery rolemodel alignment

## Scope

MVP04-FIX corrects the manual operator evidence-reference detour and aligns ETF EU delivery with the `weekly-etf` workflow model.

## Current issue

MVP04 stopped at `OPERATOR_ACTION_REQUIRED` and asked the operator to fill non-secret evidence references. That is not how the `weekly-etf` rolemodel works.

## Root cause

The EU workflow already has a delivery skeleton, but it was still named and framed as bootstrap validation only. The manual evidence route was therefore unnecessary and confusing.

## Recommended change implemented

The existing ETF EU workflow now has a rolemodel-style `workflow_dispatch` input:

```text
delivery_mode=validate_only|dry_run|send
```

Push-triggered runs remain `validate_only`.

## Rolemodel alignment

The EU workflow now declares the same SMTP/mail secret names used by the rolemodel send workflow:

```text
MRKT_RPRTS_SMTP_HOST
MRKT_RPRTS_SMTP_PORT
MRKT_RPRTS_SMTP_USER
MRKT_RPRTS_SMTP_PASS
MRKT_RPRTS_MAIL_FROM
MRKT_RPRTS_MAIL_TO
MRKT_RPRTS_MAIL_TO_NL
```

No secret values are exposed.

## Safety boundary

`delivery_mode=send` is declared but intentionally blocked until an EU-specific sender entrypoint is validated.

`delivery_mode=dry_run` is available for workflow-based report, validation evidence, delivery manifest, and run bundle generation without email delivery.

## Files changed

```text
.github/workflows/send-weekly-etf-eu-report.yml
control/ETF_EU_MVP04_FIX_WEEKLY_ETF_DELIVERY_ROLEMODEL_ALIGNMENT_V1.md
output/client_surface/etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment_20260704_000000.json
output/client_surface/etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment_notes_20260704_000000.md
```

## Decision

```text
manual_evidence_route_superseded=true
operator_reference_template_required_for_delivery=false
operator_hash_requirement_removed=true
workflow_delivery_mode_input_created=true
dry_run_mode_declared=true
send_mode_declared=true
send_mode_blocked_until_eu_sender_validated=true
selected_next_step=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN
```

## Next step

Run the ETF EU workflow manually with:

```text
delivery_mode=validate_only
```

If green, run:

```text
delivery_mode=dry_run
```

Do not use `delivery_mode=send` until an EU sender entrypoint is validated.
