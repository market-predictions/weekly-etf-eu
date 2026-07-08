# ETF EU MVP04-FIX weekly-etf delivery rolemodel alignment v1

## Purpose

Correct the MVP04 manual evidence-reference detour and align ETF EU delivery with the existing `weekly-etf` delivery rolemodel.

## Scope

This package is a corrective workflow-alignment package. It does not create a new manual evidence process and does not create ETF-EU-MVP05.

## Rolemodel authority

The `weekly-etf` rolemodel uses GitHub Actions workflow execution, repository secrets, report validation, delivery manifest evidence, run manifest evidence, and artifact commits. It does not require the operator to commit recipient hashes or delivery references into control files.

## EU correction

ETF EU already has a delivery skeleton:

```text
.github/workflows/send-weekly-etf-eu-report.yml
runtime/build_etf_eu_delivery_manifest.py
tools/validate_etf_eu_delivery_manifest.py
runtime/build_etf_eu_run_bundle.py
```

The correction is to align that skeleton with the rolemodel while preserving EU safety boundaries.

## Workflow change

The EU workflow now has an explicit `workflow_dispatch` input:

```text
delivery_mode=validate_only|dry_run|send
```

Default behavior remains safe:

```text
push events => validate_only
workflow_dispatch default => validate_only
```

## Secret-name alignment

The workflow now declares the same SMTP/mail secret names used by the rolemodel in the send guard:

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

## Send boundary

`delivery_mode=send` is intentionally blocked by MVP04-FIX until an EU-specific sender entrypoint is validated.

## Dry-run boundary

`delivery_mode=dry_run` builds the existing report, validation evidence, delivery manifest, and run bundle. It does not send email.

## Manual evidence-route correction

The manual operator evidence reference route is superseded by workflow-based delivery alignment. Do not require the operator to fill `control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md` before using the delivery workflow.

## What changed

```text
manual_evidence_route_superseded=true
workflow_delivery_mode_input_created=true
rolemodel_secret_names_declared=true
send_mode_declared_but_blocked=true
dry_run_mode_declared=true
validate_only_default=true
production_delivery=false
email_delivery=false
manual_operator_hash_requirement=false
selected_next_step=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN
```

## What did not change

```text
portfolio_mutation=false
funding_authority=false
valuation_grade=false
candidate_promotion=false
production_send=false
secret_values_exposed=false
recipient_plaintext_values_exposed=false
```

## Next step

Run the existing ETF EU workflow manually using `delivery_mode=validate_only` first. If green, run it with `delivery_mode=dry_run`. Do not use `delivery_mode=send` until an EU sender entrypoint has been explicitly validated.
