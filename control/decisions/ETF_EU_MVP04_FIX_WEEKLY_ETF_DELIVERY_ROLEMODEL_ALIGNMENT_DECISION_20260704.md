# ETF-EU-MVP04-FIX weekly-etf delivery rolemodel alignment decision — 2026-07-04

## Decision

MVP04-FIX supersedes the manual operator evidence-reference route and aligns ETF EU delivery with the existing `weekly-etf` workflow rolemodel.

## Authority

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-MVP04-FIX
source_work_package=ETF-EU-MVP04
status=completed_rolemodel_delivery_alignment
manual_evidence_route_superseded=true
operator_reference_template_required_for_delivery=false
operator_hash_requirement_removed=true
workflow_delivery_mode_input_created=true
delivery_mode_default=validate_only
delivery_mode_options=validate_only,dry_run,send
push_delivery_mode=validate_only
dry_run_mode_declared=true
send_mode_declared=true
send_mode_blocked_until_eu_sender_validated=true
rolemodel_secret_names_declared=true
private_values_exposed=false
recipient_values_exposed=false
selected_next_package=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN
```

## Artifacts created

```text
control/ETF_EU_MVP04_FIX_WEEKLY_ETF_DELIVERY_ROLEMODEL_ALIGNMENT_V1.md
output/client_surface/etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment_20260704_000000.json
output/client_surface/etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment_notes_20260704_000000.md
tools/validate_etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment.py
tests/test_etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment.py
```

## Workflow updated

```text
.github/workflows/send-weekly-etf-eu-report.yml
```

## Decision interpretation

```text
The operator does not need to fill the manual evidence-reference template for delivery.
The existing ETF EU workflow is now the active operational path.
The workflow is safe by default with delivery_mode=validate_only.
delivery_mode=dry_run may be used after validate_only is green.
delivery_mode=send remains blocked until an EU-specific sender entrypoint is validated.
No production delivery was performed by this package.
No delivery success was claimed by this package.
```

## Next step

```text
RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN — run the ETF EU workflow with delivery_mode=validate_only, then dry_run if green.
```
