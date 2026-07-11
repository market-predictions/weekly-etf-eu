# ETF EU Current Package Transport Runner Contract V1

Date: 2026-07-11  
Repository: `market-predictions/weekly-etf-eu`  
Contract id: `ETF_EU_CURRENT_PACKAGE_TRANSPORT_RUNNER_CONTRACT_V1`

## Purpose

Define the transport runner adapter for the authorized current-package Weekly ETF EU delivery chain.

```text
upstream_pattern_adapted=weekly-etf transport and manifest-evidence concepts; adapted for EU current-package queue authority and redacted evidence
```

MVP28D is a production-path adapter package. It does not re-open authorization and it does not execute live transport by itself.

## Current package authority

The runner must start from:

```text
control/run_queue/etf_eu_current_package_delivery_request_20260710_000000.md
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/delivery_authorization/etf_eu_guarded_send_authorization_20260710_000000.json
output/delivery_control/etf_eu_delivery_workflow_wiring_20260710_000000.json
```

Required authority flags:

```text
ready_for_controlled_delivery=true
delivery_authorized=true
send_command_allowed=true
run_queue_allowed=true
run_queue_created=true
```

Rejected as authority:

```text
legacy MVP19/FIX2-only ready artifacts
legacy 20260709 hardcoding
U.S. report discovery
U.S. recipient authority
U.S. delivery authority
plaintext recipients in repo files
provider credentials in repo files
raw receipt material in GitHub
```

## Runner modes

The runner supports:

```text
dry_run
send
```

Dry-run mode must write result/evidence artifacts without outbound transport:

```text
transport_attempted=false
transport_success=false
receipt_confirmed=false
delivery_status=dry_run_no_transport
```

Send mode is available only through an explicit guarded workflow branch. It may attempt transport only when runtime environment values are present and the workflow confirmation is set. Transport success is not receipt confirmation.

## Evidence policy

The runner must produce redacted evidence only. Evidence must preserve:

```text
recipient_plaintext_values_exposed=false
secret_values_exposed=false
raw_receipt_pdf_stored_in_github=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

The delivery caveat is mandatory:

```text
SMTP success is not an end-recipient inbox receipt.
```

## Handoff

If the runner and workflow adapter are created but live transport is not executed, the next package is:

```text
ETF-EU-MVP28E_GUARDED_CURRENT_PACKAGE_DRY_RUN_OR_SEND_EXECUTION
```
