# Weekly ETF EU Review OS — Next Actions

## Current priority

```text
ROUTINE_IDLE_READY_FOR_NEXT_FRESH_CYCLE
```

## Closed maintenance repair

The post-delivery email equity-curve parity defect is closed.

```text
issue=105 CLOSED
pull_request=106 MERGED
assured_candidate_head=57fef69626951f2a33bc63ced25253bcc4e84df0
merge_commit=1fb7168f7ba433e138503c68aa9447c5f7ebbc65
independent_assurance_issue=108 CLOSED
independent_assurance_verdict=PASS
workpackage=ETF-EU-EMAIL-EQUITY-PARITY-105 CLOSED
corrected_resend_authorized=false
corrected_resend_executed=false
principal_decision_required=false
```

The active graph-delivery contract now follows the established Weekly ETF donor pattern: deterministic PNG before SMTP, embedded PNG in final standalone HTML, final PDF regenerated from that HTML, and the identical approved PNG bytes reused through MIME `cid:equitycurve`. Controlled transport performs no chart redraw/rasterization and fails closed on residual SVG or missing/ambiguous/malformed PNG media.

## No remaining action for the 2026-08-14 cycle

The previously delivered 2026-08-14 report remains closed and receipt-confirmed. The rendering repair does not reopen that report cycle and does not authorize a resend.

There is no remaining report production, assurance, merge, delivery, receipt or governance-closeout step for that historical cycle.

## Next normal fresh cycle

The next Weekly ETF EU production cycle must begin only when a new completed-close date is due. It must:

- start from fresh completed-close evidence;
- treat prior reports only as historical strategy/model context;
- perform a full current portfolio re-underwrite rather than mechanically rolling positions forward;
- use the current donor-aligned equity graph contract for HTML/PDF/email parity;
- preserve independent assurance before merge;
- preserve exact approved-artifact/hash binding before any controlled transport;
- require a separate current guarded-send authority for any actual email delivery;
- claim delivery success only from positive recipient-side receipt/attachment evidence or equivalent real delivery receipt/manifest.

## Protected boundaries

- no real broker execution;
- no share/cash mutation without explicit current allocation-decision authority;
- no hard position-count target;
- no retired 50%/35%/15% allocation limits;
- no research-only mapping/price becomes funding authority automatically;
- candidate generation has no SMTP/delivery authority;
- no rerender after artifact approval;
- no resend of historical reports from architecture/maintenance authority;
- no delivery success claim without a real receipt/manifest.

## Controller housekeeping

The project-local state is reconciled through the completed email-parity merge. Central `market-predictions/control-plane` cache/narrative entries may still be stale until their next portfolio-control reconciliation; project-local/live GitHub evidence remains authoritative.
