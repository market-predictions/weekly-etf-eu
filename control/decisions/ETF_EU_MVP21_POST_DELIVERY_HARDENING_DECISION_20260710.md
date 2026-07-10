# Decision — ETF-EU-MVP21 Post-Delivery Hardening

Date: 2026-07-10  
Repository: `market-predictions/weekly-etf-eu`  
Decision id: `ETF_EU_MVP21_POST_DELIVERY_HARDENING_DECISION_20260710`

## Decision

Harden the EU delivery closeout loop by adapting the mature upstream `weekly-etf` delivery-manifest and run-manifest pattern to the EU/UCITS receipt-confirmed resend.

```text
upstream_pattern_adapted=weekly-etf delivery manifest and run manifest closeout pattern; adapted for EU manual Gmail receipt and UCITS authority boundaries
```

## Upstream basis

The upstream `weekly-etf` delivery workflow writes a redaction-safe delivery manifest after SMTP send, writes a final run manifest, validates manifest evidence, and commits run artifacts.

Relevant upstream concepts:

```text
weekly-etf:.github/workflows/send-weekly-report.yml
weekly-etf:tools/write_etf_delivery_manifest_summary.py
weekly-etf:tools/write_weekly_etf_run_manifest.py
weekly-etf:tools/validate_etf_manifest_evidence.py
```

## EU adaptation

The first EU guarded resend was already closed with a manual Gmail inbox receipt supplied by the user. MVP21 adds a first-class EU closeout manifest so that this receipt-confirmed state is deterministic and repo-persisted without storing the raw Gmail PDF.

New EU closeout path:

```text
output/delivery/etf_eu_manual_receipt_confirmation_20260710_1755.json
+ output/delivery_package/etf_eu_delivery_package_manifest_20260709_000000.json
+ output/client_surface/etf_eu_mvp19_fix2_ready_for_controlled_resend_20260709_000000.json
→ tools/write_etf_eu_delivery_closeout_manifest.py
→ output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json
→ output/run_manifests/latest_etf_eu_delivery_closeout_manifest_path.txt
→ tools/validate_etf_eu_delivery_closeout_manifest.py
```

## Authority rules

The closeout manifest may confirm the completed guarded resend and manual inbox receipt.

It must not create:

```text
valuation_grade=true
funding_authority=true
portfolio_mutation=true
production_delivery_authority=true
```

The raw Gmail PDF is not stored in GitHub. Recipient values and secrets remain redacted.

## Future-send hardening

Future guarded sends must persist machine-readable evidence files in GitHub or fail. The workflow now requires exact evidence files to exist, stages them with `git add -f`, fails if nothing is staged, verifies tracked files after push, and requires `message_id_or_receipt_reference`.

## Consequence

`ETF-EU-MVP21_POST_DELIVERY_HARDENING` may close as:

```text
status=completed_post_delivery_hardening
selected_next_package=ETF-EU-MVP22_ROUTINE_WEEKLY_EU_REPORT_OPERATING_LOOP
```

MVP22 should move from one-off controlled resend rescue work to the routine weekly EU report operating loop.
