# ETF EU Email Equity Parity — Issue 105

## Identity

```text
workpackage_id=ETF-EU-EMAIL-EQUITY-PARITY-105
claim_id=ETF-EU-EMAIL-EQUITY-PARITY-105
issue=105
pull_request=106
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-email-equity-parity-105
trusted_base_main_sha=d9b4ecac4f49417fd7430b01303d1c3425b7074a
assured_candidate_head_sha=57fef69626951f2a33bc63ced25253bcc4e84df0
merge_commit_sha=1fb7168f7ba433e138503c68aa9447c5f7ebbc65
owner_role=implementation_operations
status=CLOSED
opened_at=2026-08-18T06:52:23Z
closed_at=2026-08-18T13:03:59Z
independent_assurance_issue=108
independent_assurance_comment=5328420726
independent_assurance_verdict=PASS
principal_decision_required=false
```

## Current issue

The delivered 2026-08-14 Weekly ETF EU PDF rendered the portfolio equity curve, while Gmail did not render the same curve from the delivered HTML email. The delivered MIME contained the curve as inline SVG.

## Root cause

The EU delivery surface had diverged from the established `market-predictions/weekly-etf` donor contract. The report renderer produced inline SVG and the controlled sender passed that representation through as email HTML, while Gmail did not reliably render it.

## Decision framework

Adopt the established donor graph-delivery architecture rather than maintain a separate EU-specific transport design.

```text
portfolio/equity state
-> deterministic PNG before SMTP transport
-> standalone NL/EN HTML embeds the PNG as data:image/png;base64
-> final PDF is regenerated from that final HTML
-> controlled sender reuses the identical approved PNG bytes as cid:equitycurve
-> no redraw/rasterization in SMTP transport
-> fail closed on residual SVG, absent/ambiguous PNG, malformed base64 or non-PNG payload
```

Donor authority used as design precedent:

```text
market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af
runtime/equity_curve_png_contract.py
runtime/standalone_html_equity_embed.py
control/decisions/REPORT_FRESHNESS_AND_STANDALONE_HTML_EQUITY_DECISION_20260716.md
```

EU historical precedent `runtime/send_etf_eu_shadow_cid_delivery.py` remains historical only; the disabled shadow workflow was not reactivated.

## Input/state contract

- Current EU/UCITS portfolio/equity state remains authoritative.
- Historical reports are context only, not current-price authority.
- No portfolio, pricing, allocation, trade-ledger or broker state was changed by this repair.
- Guarded-delivery authority remains separate from merge authority.

## Output contract

When `equity_curve.show_chart=true`:

- final standalone NL/EN HTML contains exactly one embedded PNG equity curve;
- final PDF consumes the same final HTML surface;
- controlled email HTML contains exactly one `cid:equitycurve` reference;
- MIME contains exactly one matching inline `image/png` related part;
- MIME PNG bytes equal the PNG bytes embedded in the approved HTML;
- residual SVG, missing/ambiguous PNG or malformed/non-PNG data fails closed.

When no chart is required, no graph is invented.

## Implemented files

- `runtime/equity_curve_png_contract.py`
- `runtime/standalone_html_equity_embed.py`
- `runtime/finalize_etf_eu_client_surface_semantics.py`
- `runtime/equity_curve_eu_contract.py`
- `runtime/send_etf_eu_controlled_report.py`
- `.github/workflows/run-weekly-etf-eu-routine.yml`
- `.github/workflows/test-etf-eu-email-equity-parity.yml`
- `.github/workflows/validate-etf-eu-donor-parity.yml`
- `tests/test_etf_eu_email_equity_parity.py`
- `tests/test_etf_eu_guarded_delivery_authority.py` fixture alignment only

The active controlled transport workflow retained its existing main-only, independently assured authority, artifact-hash binding and two explicit send-confirmation controls.

## Exact-head validation and assurance

```text
candidate_head_sha=57fef69626951f2a33bc63ced25253bcc4e84df0
email_equity_parity_run=32133189274 result=SUCCESS
donor_parity_full_package_run=32133189340 result=SUCCESS
product_boundary_run=32133189275 result=SUCCESS
release_evidence_preflight_run=32133189278 result=SUCCESS
independent_assurance_issue=108
independent_assurance_comment=5328420726
independent_assurance_verdict=PASS
findings=[]
```

Immediately before merge, live PR head remained the assured candidate and live `main` remained the trusted base. PR #106 was merged with expected-head protection.

## Integration result

```text
pr_106=MERGED
merge_commit_sha=1fb7168f7ba433e138503c68aa9447c5f7ebbc65
issue_105=CLOSED
issue_108=CLOSED
portfolio_mutation=false
pricing_mutation=false
allocation_mutation=false
trade_ledger_mutation=false
broker_execution=false
report_resend=false
smtp_delivery_authority=false
```

## Stable boundary

The PASS and merge repair future delivery representation only. They do not authorize retransmission of the already-delivered 2026-08-14 report. Any future send remains subject to the normal guarded-delivery authority, controlled transport and real receipt/closeout chain.

## Final status

```text
donor_aligned_repair=COMPLETE
exact_head_assurance=PASS
merge=COMPLETE
claim=CLOSED
corrected_resend=NOT_AUTHORIZED_NOT_EXECUTED
next_state=ROUTINE_IDLE_READY_FOR_NEXT_FRESH_CYCLE
```
