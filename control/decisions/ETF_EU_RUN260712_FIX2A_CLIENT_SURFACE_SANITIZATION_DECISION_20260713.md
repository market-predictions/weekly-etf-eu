# ETF EU RUN260712 FIX2A — Client-Surface Sanitization Decision

Date: 2026-07-13  
Repository: `market-predictions/weekly-etf-eu`

## Decision

The PDF renderer introduced in FIX1 is structurally valid, but the first corrected client package is not authorized for live resend because it exposes internal machine-state and authority metadata.

The package under correction control id `20260713_000000` is superseded. Its files, hashes and dry-run evidence remain immutable historical evidence, but `live_send_allowed=false`.

## Root cause

The native routine report builder copied structured verification enums directly into the client table and generated an `Authority flags` section in client Markdown. The PDF validator then incorrectly required those internal values to appear in the client PDF.

Visual completeness therefore did not equal client-surface acceptability.

## Upstream pattern adapted

`market-predictions/weekly-etf` was inspected first. The adapted concepts are:

- native client language generated correctly at source;
- narrow deterministic aliases for structured state labels;
- forbidden-token validation after generation;
- separation between client output and internal state/evidence;
- no broad arbitrary prose translation in the renderer.

U.S. holdings, U.S. portfolio state, U.S. ticker authority, U.S. recipients and U.S. report sections were not copied.

## Required output contract

Client Markdown, HTML, PDF and email body must not contain raw verification enums, transport-state flags, authority-state flags or the `Authority flags` section.

The same authority values remain preserved in JSON package, run, delivery and control evidence.

The client report ends at section 7. Machine validation now requires:

```text
client_surface_clean=true
authority_metadata_absent=true
raw_status_enums_absent=true
```

## Supersession

```text
superseded_correction_control_id=20260713_000000
superseded=true
live_send_allowed=false
superseded_by_sanitization_run_id=20260713_180000
superseded_by_correction_control_id=20260713_180000
```

No historical evidence is deleted or overwritten.

## Operational boundary

FIX2A creates a preview-only sanitization run, machine and visual evidence, authority-separation evidence, a new correction package, and a new dry run. It stops before live transport.

No email was sent and no receipt check was performed as part of this decision.
