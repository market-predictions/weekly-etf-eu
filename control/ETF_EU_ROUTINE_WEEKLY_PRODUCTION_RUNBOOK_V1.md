# ETF EU Routine Weekly Production Runbook V1

Date: 2026-07-12  
Repository: `market-predictions/weekly-etf-eu`

This is the authoritative operational runbook for fresh generation, validation, guarded delivery, delayed receipt verification and production closeout of routine Weekly ETF EU reports.

## Phase 1 — Session start and authority

1. Read `control/SYSTEM_INDEX.md`.
2. Read `control/CURRENT_STATE.md`.
3. Read `control/NEXT_ACTIONS.md`.
4. Inspect the closest `market-predictions/weekly-etf` implementation before changing EU machinery.
5. Keep `weekly-etf-eu` as EU/UCITS source of truth.
6. Create a new `run_id`, `report_date` and `report_suffix`.
7. Never reuse a previous run's dated queue, manifests or evidence as current-run authority.

## Phase 2 — Current data and state

1. Obtain current pricing and market inputs.
2. Validate UCITS identity through the EU registry and ISIN-first rules.
3. Treat previous reports as historical strategy context only.
4. Use current EU portfolio state as authority.
5. Do not fund or promote an ETF without required pricing and investability evidence.
6. Produce current-run pricing, state and analysis artifacts.

## Phase 3 — Generation and output validation

1. Generate Dutch-primary Markdown, HTML and PDF.
2. Generate English companion Markdown, HTML and PDF.
3. Create the current fresh-generation package manifest.
4. Run content, pricing, leakage, bilingual and client-surface validators.
5. Confirm the package contains all required current-run files.
6. Reject stale report-date or run-id paths.

## Phase 4 — Delivery preparation

1. Create the current-run delivery preparation artifact.
2. Confirm `delivery_authorized` and `send_command_allowed` for that run.
3. Create and validate a current-run queue artifact.
4. Use validate-only or dry-run after workflow/runtime changes.
5. An unchanged routine path may proceed to guarded delivery after all gates pass.

## Phase 5 — Guarded delivery

1. Use the current-package EU workflow.
2. Select the delivery branch explicitly.
3. Use the current run's queue path.
4. Require the guarded confirmation value.
5. Persist the current-run transport result and delivery evidence.
6. Require `transport_attempted=true` and `transport_success=true` before proceeding.
7. Treat SMTP success only as transport-layer evidence.

## Phase 6 — Delayed receipt verification

Independent delayed receipt verification is mandatory.

1. Wait approximately 10 minutes after successful transport.
2. Search the connected receipt mailbox/API for the matching current-run message.
3. Match using run/date evidence, hashed identity fields and expected attachments.
4. Confirm Dutch PDF, English PDF, Dutch HTML and English HTML.
5. Store only hashes, timestamps and booleans.
6. Never store raw mailbox content, addresses, subjects or headers.
7. Keep `receipt_confirmed=false` if independent evidence is not found.
8. Use delayed recheck rather than automatic resend.

## Phase 7 — Closeout

1. Create or update the routine run manifest.
2. Create the production delivery closeout manifest.
3. Require `transport_success=true`.
4. Require `receipt_confirmed=true` for completed production closeout.
5. Record blockers explicitly.
6. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`.
7. Never claim completed delivery without both transport and receipt artifacts.

## Failure routing

```text
generation or validation failure -> repair current run; do not deliver
dry-run failure -> repair workflow/runtime; do not deliver
guarded transport failure -> investigate before creating another queue
transport success but no receipt -> delayed receipt recheck; do not resend automatically
receipt mismatch or missing attachments -> delivery evidence investigation
successful transport plus confirmed receipt -> production closeout
```

## Routine completion definition

A routine weekly run is complete only when:

```text
fresh current-run package exists
all required validators passed
guarded delivery executed
transport result exists
transport_success=true
delivery evidence exists
independent receipt evidence exists
receipt_confirmed=true
all expected attachments were observed
routine manifest updated
closeout manifest created
```

## Operating rule

Architecture work packages are created only for a specific defect or material capability change. A normal new weekly report is a routine operation under this runbook.
