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
status=HANDOVER_READY
opened_at=2026-08-18T06:52:23Z
last_reconciled_at=2026-08-18T11:40:00Z
last_reconciled_claim_head_sha=ade3d9b3c59d1b68502fa54c85692886f31dc8eb
principal_decision_required=false
```

`last_reconciled_claim_head_sha` is the live PR head observed at the final implementation reconciliation immediately before this metadata-only handover update; it is not a self-referential promise. Independent assurance must reconstruct and freeze the live PR #106 head again before review. Previous assurance request #107 is terminal and was withdrawn before any review because the first implementation was superseded by donor alignment.

## Current issue
The canonical 2026-08-14 HTML and delivered RFC822 MIME both contained the equity curve as inline SVG, while the recipient Gmail HTML surface did not render it. The corresponding PDF rendered the same curve correctly.

## Root cause
The EU client surface had regressed from the established donor delivery contract. The active EU renderer produced an inline SVG and the controlled sender passed that representation through to the HTML MIME alternative. Gmail did not reliably render that representation.

This was not a novel design problem. The authoritative donor repository already separates graph rendering from delivery-surface representation:
- `market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af/runtime/equity_curve_png_contract.py` materializes and validates a PNG graph asset;
- `runtime/standalone_html_equity_embed.py` uses an embedded PNG data URI for standalone HTML and `cid:equitycurve` for MIME email;
- `control/decisions/REPORT_FRESHNESS_AND_STANDALONE_HTML_EQUITY_DECISION_20260716.md` records that split as an explicit product decision;
- this EU repository itself retains historical precedent in `runtime/send_etf_eu_shadow_cid_delivery.py`, which converts one embedded PNG data URI into one CID-related `image/png` part and fails closed on ambiguity.

## Decision framework
Adopt the established donor delivery contract rather than maintain an EU-specific transport invention.

The implemented architecture is:
1. deterministic portfolio-curve PNG materialization before SMTP transport;
2. final standalone/client HTML is self-contained and carries the graph as an embedded PNG data URI;
3. final PDF is rendered from that same final client HTML;
4. MIME email replaces exactly that one approved data URI with `cid:equitycurve` and attaches the identical PNG bytes as `image/png` under `multipart/related`;
5. controlled transport does not redraw or rasterize the graph;
6. ambiguous, absent, malformed or residual-SVG graph representations fail closed when a graph is expected.

The superseded first PR implementation that rasterized inline SVG with CairoSVG inside the controlled sender remains diagnostic history only and is not the final design.

## Input/state contract
- exact current base/main observed at final implementation reconciliation: `d9b4ecac4f49417fd7430b01303d1c3425b7074a`;
- current portfolio/equity-curve state remains authoritative; no historical report is current-price authority;
- no portfolio, pricing, allocation, trade-ledger or broker state is changed by this repair;
- donor architecture is design precedent; EU/UCITS identity, pricing, allocation and guarded-delivery authority remain local to this repository.

## Output contract
When `equity_curve.show_chart=true`:
- final assured standalone NL/EN HTML contains exactly one embedded `data:image/png;base64,...` portfolio curve;
- final PDF is regenerated from the same final HTML and therefore consumes that same PNG surface;
- controlled email HTML contains exactly one `cid:equitycurve` reference and no embedded data URI for that graph;
- the MIME message contains exactly one matching inline `image/png` related part;
- MIME PNG bytes equal the PNG bytes embedded in the approved HTML;
- graph bytes are not generated or mutated after delivery authority is established;
- residual inline SVG, missing PNG, ambiguous PNG or malformed base64/PNG blocks message construction.

When the equity-curve contract says no chart is required, no graph image is invented.

## Implemented files
- `runtime/equity_curve_png_contract.py` — donor-derived deterministic PNG rendering and visual integrity validation.
- `runtime/standalone_html_equity_embed.py` — final standalone HTML data-URI materialization and fail-closed validation.
- `runtime/finalize_etf_eu_client_surface_semantics.py` — invokes PNG materialization before final HTML is persisted and before final PDF regeneration.
- `runtime/equity_curve_eu_contract.py` — distinguishes intermediate SVG from final embedded-PNG surface.
- `runtime/send_etf_eu_controlled_report.py` — translates the approved embedded PNG bytes to `cid:equitycurve`; no send-time rasterization.
- `.github/workflows/run-weekly-etf-eu-routine.yml` — installs the already-pinned donor-compatible `matplotlib==3.9.2` during candidate generation.
- `.github/workflows/send-weekly-etf-eu-controlled-transport.yml` — no rasterizer dependency; authority and double-confirmation controls remain intact.
- `tests/test_etf_eu_email_equity_parity.py` — NL/EN standalone PNG, byte-identical MIME CID reuse and fail-closed regressions.
- `.github/workflows/test-etf-eu-email-equity-parity.yml` — dedicated graph-delivery parity gate.
- `.github/workflows/validate-etf-eu-donor-parity.yml` — exercises the donor-aligned graph contract inside the broad/full-package suite.
- `tests/test_etf_eu_guarded_delivery_authority.py` — earlier stale fixture alignment to the already-authoritative `client_surface_safety` contract; no product behavior change.

## Exact implementation validation evidence

```text
validated_implementation_head=ade3d9b3c59d1b68502fa54c85692886f31dc8eb
base_main_sha=d9b4ecac4f49417fd7430b01303d1c3425b7074a
email_equity_parity_run=32132804210 result=SUCCESS
product_boundary_run=32132804084 result=SUCCESS
release_evidence_preflight_run=32132804146 result=SUCCESS
donor_parity_full_package_run=32132804121 result=SUCCESS
portfolio_mutation=false
pricing_mutation=false
allocation_mutation=false
trade_ledger_mutation=false
broker_execution=false
resend_executed=false
```

The final work-package update is metadata-only. Its descendant live PR head still requires exact-head CI reconstruction by assurance before review.

## Operational runbook remaining
1. Reconstruct live PR #106 head and current base/main from GitHub.
2. Require all relevant exact-head PR gates green on that live head.
3. Perform a fresh blind-first independent `governance_release_assurance`; do not reuse #107.
4. Merge only the unchanged independently PASSed exact head.
5. After merge, reconcile `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md` and the stable decision/defect history.
6. Do not resend the already-delivered report without a separate governed send authorization and real delivery receipt/manifest.

## Current acceptance status
- demonstrated root cause: CONFIRMED;
- donor precedent reconstructed: CONFIRMED;
- EU-local historical CID precedent reconstructed: CONFIRMED;
- donor-aligned implementation: COMPLETE;
- validated implementation head gates: ALL SUCCESS;
- PR #106: HANDOVER_READY / awaiting fresh exact-head assurance;
- previous assurance #107: CLOSED / SUPERSEDED BEFORE REVIEW;
- independent exact-head assurance on final live head: PENDING;
- merge: NOT AUTHORIZED;
- corrected resend: NOT AUTHORIZED / NOT EXECUTED.
