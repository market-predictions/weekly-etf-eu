# ETF EU Email Equity Parity — Issue 105

## Identity

```text
workpackage_id=ETF-EU-EMAIL-EQUITY-PARITY-105
claim_id=ETF-EU-EMAIL-EQUITY-PARITY-105
issue=105
pull_request=106
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-email-equity-parity-105
base_main_sha=d9b4ecac4f49417fd7430b01303d1c3425b7074a
owner_role=implementation_operations
status=ACTIVE
opened_at=2026-08-18T06:52:23Z
last_reconciled_at=2026-08-18T11:29:37Z
last_reconciled_claim_head_sha=5d4fc0308f0876502d91d4cfa81141498f522f07
principal_decision_required=false
```

`last_reconciled_claim_head_sha` is an observed reconciliation value, not a self-referential promise. The previous assurance request #107 was withdrawn before review because the implementation is being reconciled to the established donor architecture.

## Current issue
The canonical 2026-08-14 HTML and delivered RFC822 MIME both contain the equity curve as inline SVG, while the recipient Gmail HTML surface does not render it. The corresponding PDF renders the same curve correctly.

## Root cause
The EU client surface regressed from the established donor delivery contract. The current EU renderer emits the portfolio curve as inline SVG and `runtime/send_etf_eu_controlled_report.py` sends that representation as the HTML MIME alternative. Gmail does not reliably render that representation.

This is not a novel design problem. The authoritative donor repository already separates graph rendering from delivery-surface representation:
- `market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af/runtime/equity_curve_png_contract.py` materializes and validates a PNG graph asset;
- `runtime/standalone_html_equity_embed.py` uses an embedded PNG data URI for standalone HTML and `cid:equitycurve` for MIME email;
- `control/decisions/REPORT_FRESHNESS_AND_STANDALONE_HTML_EQUITY_DECISION_20260716.md` records that split as an explicit product decision;
- the EU repository itself retains the historical `runtime/send_etf_eu_shadow_cid_delivery.py` precedent, which converts one embedded PNG data URI into one CID-related `image/png` part and fails closed on ambiguity.

## Decision framework
Adopt the established donor delivery contract rather than keep an EU-specific transport invention.

The target architecture is:
1. one deterministic portfolio-curve PNG representation derived before SMTP transport;
2. standalone/client HTML is self-contained and carries the graph as an embedded PNG data URI;
3. MIME email replaces exactly that one data URI with `cid:equitycurve` and attaches the identical PNG bytes as `image/png` under `multipart/related`;
4. PDF and HTML remain semantically identical and are generated before guarded delivery authority;
5. ambiguous, absent or malformed graph materialization fails closed when the report state requires a graph.

The previous PR-head implementation that rasterized inline SVG with CairoSVG inside the controlled sender is superseded as the final design. It remains diagnostic evidence only.

## Input/state contract
- exact base at claim creation: `d9b4ecac4f49417fd7430b01303d1c3425b7074a`;
- current portfolio/equity-curve state remains authoritative; no historical report is current-price authority;
- no portfolio, pricing, allocation, trade-ledger or broker state may be changed by this repair;
- donor architecture is design precedent only; EU/UCITS state and authority boundaries remain local to this repository.

## Output contract
When `equity_curve.show_chart=true`:
- the final assured standalone NL/EN HTML contains exactly one embedded `data:image/png;base64,...` portfolio curve;
- the final assured PDF contains the same graph presentation;
- controlled email HTML contains exactly one `cid:equitycurve` reference and no embedded data URI for that graph;
- the MIME message contains exactly one matching inline `image/png` related part;
- graph bytes are not generated or mutated after delivery authority is established;
- any missing/ambiguous/malformed graph representation blocks controlled message construction.

When the equity-curve contract says no chart is required, no graph image is invented.

## Operational runbook
1. Keep PR #106 in draft while donor alignment is implemented.
2. Reuse/adapt the donor PNG + standalone-data-URI + MIME-CID pattern and the EU shadow-CID precedent; do not reactivate the disabled shadow workflow.
3. Remove send-time SVG rasterization from the final controlled transport path.
4. Add/adjust NL/EN regression coverage for standalone HTML, PDF parity and MIME CID binding.
5. Re-run product-boundary, donor-parity/full-package and email-parity gates on the new exact head.
6. Freeze the new exact head and create a fresh blind-first assurance request; #107 is terminal/superseded.
7. Merge only an unchanged independently PASSed head.
8. Do not resend the already-delivered report without a separate governed send action.

## Current acceptance status
- demonstrated root cause: CONFIRMED;
- donor precedent reconstructed: CONFIRMED;
- EU-local historical CID precedent reconstructed: CONFIRMED;
- previous send-time CairoSVG implementation: SUPERSEDED AS FINAL DESIGN;
- donor-aligned implementation: IN PROGRESS;
- PR #106: DRAFT;
- previous assurance #107: CLOSED / SUPERSEDED BEFORE REVIEW;
- independent exact-head assurance: NOT YET REQUESTED FOR REVISED HEAD;
- merge: NOT AUTHORIZED;
- corrected resend: NOT AUTHORIZED / NOT EXECUTED.
