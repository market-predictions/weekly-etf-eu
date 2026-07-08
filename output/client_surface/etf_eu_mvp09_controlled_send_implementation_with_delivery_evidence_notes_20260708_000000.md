# ETF-EU-MVP09 evidence implementation notes

## Scope

MVP09 adds the evidence writer and validators for the EU report chain.

## Files

```text
runtime/write_etf_eu_delivery_evidence.py
tools/validate_etf_eu_delivery_evidence.py
tools/validate_etf_eu_run_bundle_delivery_evidence.py
output/delivery/etf_eu_delivery_evidence_20260708_000000.json
output/runs/20260708_000000/etf_eu_run_bundle_delivery_evidence_fixture.json
```

## Evidence fixture

```text
delivery_evidence_status=not_attempted
recipient_data_policy=redacted_hash_only
required_languages=nl,en
delivery_success=false
```

## Guardrails

```text
receipt_file_created=false
delivery_enabled=false
production_delivery=false
email_delivery=false
pdf_generation=false
delivery_receipt=false
send_performed=false
delivery_mode_send_unlocked=false
workflow_send_guard_removed=false
delivery_success_claimed=false
```

## Next package

```text
ETF-EU-MVP10 — ETF EU controlled-send workflow integration or guard replacement
```
