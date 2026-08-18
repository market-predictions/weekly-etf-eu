# Handover — ETF EU Email Equity Parity 105

```text
handover_id=HANDOVER-ETF-EU-EMAIL-EQUITY-PARITY-105-20260818
claim_id=ETF-EU-EMAIL-EQUITY-PARITY-105
from_owner_or_role=implementation_operations
to_owner_or_role=governance_release_assurance
repository=market-predictions/weekly-etf-eu
source_branch=agent/etf-eu-email-equity-parity-105
exact_source_head_sha=c6804afd162e4ea0dc2ab0d0ee656770fa6c5ad8
exact_target_or_main_sha=d9b4ecac4f49417fd7430b01303d1c3425b7074a
pull_request=106
implementation_issue=105
disposition=TRANSFER
created_at=2026-08-18T11:43:00Z
```

## Scope completed
- Reconstructed the delivered 2026-08-14 defect: PDF showed the portfolio equity curve, Gmail HTML did not, while delivered MIME contained inline SVG.
- Reconciled the implementation with the established `market-predictions/weekly-etf` donor architecture at exact donor SHA `3ffff5e6104fcc2b72ce6553718a59be2905d3af`.
- Superseded the first EU-specific send-time CairoSVG design before assurance.
- Implemented donor-standard graph delivery: deterministic PNG before transport; embedded PNG data URI in final standalone HTML; final PDF regenerated from that same HTML; identical approved PNG bytes translated to `cid:equitycurve` in MIME email.
- Added fail-closed rejection of residual SVG, absent/ambiguous embedded PNG, malformed base64 and non-PNG payloads.
- Preserved EU/UCITS portfolio, pricing, allocation, trade-ledger, broker and delivery-authority boundaries.
- Kept the historical disabled EU shadow-CID workflow disabled.

## Donor evidence
- `market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af/runtime/equity_curve_png_contract.py`
- `market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af/runtime/standalone_html_equity_embed.py`
- `market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af/control/decisions/REPORT_FRESHNESS_AND_STANDALONE_HTML_EQUITY_DECISION_20260716.md`
- EU historical precedent: `runtime/send_etf_eu_shadow_cid_delivery.py`

## Exact-head CI evidence
```text
email_equity_parity_run=32132987248 result=SUCCESS
donor_parity_full_package_run=32132987173 result=SUCCESS
product_boundary_run=32132987107 result=SUCCESS
release_evidence_preflight_run=32132987094 result=SUCCESS
```

## Unresolved items
- Independent blind-first exact-head assurance is required before merge.
- Merge is not authorized by this handover.
- Corrected resend is not authorized and has not occurred.
- After any merge, project `CURRENT_STATE`, `NEXT_ACTIONS` and stable decision/defect records still require reconciliation.

## Next action
Independent `governance_release_assurance` must reconstruct live GitHub state, verify current base/main and PR #106 exact head, review the diff and CI evidence without treating this handover narrative as proof, and issue exactly one verdict: PASS, FAIL or INDETERMINATE. A changed head invalidates the review.
