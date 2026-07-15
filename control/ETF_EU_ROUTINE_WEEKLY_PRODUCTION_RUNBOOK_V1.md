# ETF EU Routine Weekly Production Runbook V1

Date: 2026-07-15  
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

## Phase 3 — Native client generation and sanitization

1. Generate Dutch-primary client Markdown directly in natural Dutch.
2. Generate the English companion directly in client-facing English.
3. Map structured runtime statuses to controlled client labels before they enter tables.
4. Run `runtime/scrub_etf_eu_client_surface.py` as a narrow normalization and guard layer.
5. Do not use broad arbitrary prose translation in the renderer.
6. Keep internal authority and transport flags in JSON manifests and evidence only.
7. Client Markdown, HTML, PDF and email body must not contain raw machine enums or an `Authority flags` section.

Required client-surface gates:

```text
client_surface_clean=true
authority_metadata_absent=true
raw_status_enums_absent=true
```

Client reports end at the final decision-relevant section. Internal delivery state is not a client-report section.

## Phase 4 — Rendering and output validation

1. Render Dutch-primary semantic HTML and paginated PDF.
2. Render the English companion semantic HTML and paginated PDF.
3. Use `runtime/render_etf_eu_client_report.py`; plain-text PDF generation is prohibited.
4. Keep the renderer presentation-only: Markdown, HTML, CSS, typography and pagination.
5. Create the current fresh-generation package manifest.
6. Run content, pricing, leakage, bilingual and clean-client-surface validators.
7. Run Dutch and English client-grade PDF machine validation.
8. Render first, middle and last pages for visual-contract review.
9. Confirm the package contains all required current-run files.
10. Reject stale report-date or run-id paths.

### Mandatory client and PDF output contract

A routine production report may not enter guarded delivery when validation consists only of file existence, PDF header, EOF or visual completeness.

Every routine run requires:

```text
native client-safe language
deterministic structured-label normalization
forbidden-token validation
authority-evidence separation
semantic HTML rendering
Mistune table parsing
WeasyPrint PDF generation
machine PDF content validation
rendered-page visual-contract evidence
client_output_valid=true
```

The output contract must prove:

```text
all required client sections present
internal authority section absent
raw structured-state enums absent
authority and transport metadata absent from client output
semantic tables present
no raw Markdown leakage
Unicode integrity
no duplicate title
no visible clipping or overlap
```

Any renderer, sanitization or client-copy change requires explicit first/middle/last-page visual review before delivery. The visual review artifact must contain `visual_review_passed=true` and no blockers.

## Phase 5 — Delivery preparation

1. Create the current-run delivery preparation artifact.
2. Confirm `delivery_authorized` and `send_command_allowed` for that run.
3. Create and validate a current-run queue artifact.
4. Require clean-client, authority-separation, PDF machine and visual gates before creating delivery authority.
5. Use validate-only and dry-run after workflow, runtime, renderer or client-surface changes.
6. A superseded correction package is historical evidence only and may not enter live transport.
7. An unchanged routine path may proceed to guarded delivery only after all gates pass.

## Phase 6 — Guarded delivery

1. Use the current-package EU workflow or the dedicated correction workflow for an approved correction.
2. Select the delivery branch explicitly.
3. Use the current run's queue path and correction control ID.
4. Require the guarded confirmation value.
5. Revalidate package hashes and supersession state before secrets are available.
6. Persist the current-run transport result and delivery evidence.
7. Require `transport_attempted=true` and `transport_success=true` before proceeding.
8. Treat SMTP success only as transport-layer evidence.
9. SMTP success does not compensate for `client_output_valid=false` or `client_surface_clean=false`.

## Phase 7 — Delayed receipt verification

Independent delayed receipt verification is mandatory.

1. Wait approximately 10 minutes after successful transport.
2. Search the connected receipt mailbox/API for the matching current-run message.
3. Match using run/date evidence, hashed identity fields and expected attachments.
4. Confirm Dutch PDF, English PDF, Dutch HTML and English HTML.
5. Store only hashes, timestamps and booleans.
6. Never store raw mailbox content, addresses, subjects or headers.
7. Keep `receipt_confirmed=false` if independent evidence is not found.
8. Use delayed recheck rather than automatic resend.

### Existing-receipt reconciliation rule

If the expected message and attachment set have already been independently observed in the destination mailbox, do not dispatch another send merely to create or improve evidence. Reconcile the existing successful transport and receipt, create redacted receipt evidence, complete closeout, and return to routine production.

## Phase 8 — Closeout

1. Create or update the routine run manifest.
2. Create the production delivery closeout manifest.
3. Require `client_surface_clean=true`.
4. Require `transport_success=true`.
5. Require `client_output_valid=true`.
6. Require `receipt_confirmed=true` for completed production closeout.
7. Record blockers explicitly.
8. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md`.
9. Never claim completed delivery without client-output, transport and receipt artifacts.

## Failure routing

```text
generation or validation failure -> repair current run; do not deliver
client-surface or authority-separation failure -> sanitize and visually review; do not deliver
PDF machine or visual gate failure -> repair renderer/output; do not deliver
dry-run failure -> repair workflow/runtime; do not deliver
superseded package selected -> reject before secret scope
guarded transport failure -> investigate before creating another queue
transport success with invalid client output -> record defect; repair and visually approve before corrected resend
transport success but no receipt -> delayed receipt recheck; do not resend automatically
existing valid receipt found -> reconcile existing transport and receipt; do not send again
receipt mismatch or missing attachments -> delivery evidence investigation
valid clean client output plus successful transport plus confirmed receipt -> production closeout
```

## Routine completion definition

A routine weekly run is complete only when:

```text
fresh current-run package exists
all required validators passed
client_surface_clean=true
authority_separation_gate_passed=true
client_output_valid=true
PDF machine gate passed
PDF visual gate passed
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
