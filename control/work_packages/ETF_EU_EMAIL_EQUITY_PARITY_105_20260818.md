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
candidate_head_sha=2f70796037999a2cc543ecfe2df477ca02a8e324
owner_role=implementation_operations
status=HANDOVER_READY
opened_at=2026-08-18T06:52:23Z
last_reconciled_at=2026-08-18T07:00:00Z
principal_decision_required=false
```

## Current issue
The canonical 2026-08-14 HTML and delivered RFC822 MIME both contain the equity curve as inline SVG, while the recipient Gmail HTML surface does not render it. The corresponding PDF renders the same curve correctly.

## Root cause
`runtime/send_etf_eu_controlled_report.py` sends canonical HTML unchanged as the `text/html` MIME alternative. Inline SVG is therefore relied on as a client-email image representation. That is not a safe email compatibility contract.

## Decision framework
Canonical report semantics remain unchanged. The mail transport layer may derive a presentation-only email representation from the independently approved HTML, but it must preserve content and fail closed when a chart expected by the canonical HTML cannot be embedded safely.

## Input/state contract
- exact base: `d9b4ecac4f49417fd7430b01303d1c3425b7074a`;
- exact candidate: `2f70796037999a2cc543ecfe2df477ca02a8e324`;
- canonical NL/EN HTML remains the source representation;
- canonical NL/EN PDF remains unchanged;
- the equity curve is identified by `class="equity-curve-svg"` in the canonical HTML;
- no portfolio, pricing, allocation or broker state may be changed.

## Output contract
For HTML email delivery when an equity curve is present:
- the email HTML replaces the inline curve SVG with one `<img src="cid:...">` representation;
- the message contains the matching `image/png` MIME-related part;
- the CID resolves exactly once;
- the canonical HTML/PDF files are not rewritten;
- missing/failed conversion blocks message construction.

## Implemented change
1. `runtime/send_etf_eu_controlled_report.py`
   - email-only SVG→PNG materialization;
   - deterministic 920×390 conversion;
   - MIME related/CID embedding;
   - fail-closed marker/SVG/CID assertions;
   - lazy rasterizer import so unrelated validators do not acquire a new import-time dependency.
2. `.github/workflows/send-weekly-etf-eu-controlled-transport.yml`
   - pinned `CairoSVG==2.7.1` installation before controlled transport.
3. `tests/test_etf_eu_email_equity_parity.py`
   - NL/EN MIME structure, PNG signature, CID resolution, PDF preservation and fail-closed regression tests.
4. `.github/workflows/test-etf-eu-email-equity-parity.yml`
   - dedicated PR parity gate.
5. `tests/test_etf_eu_guarded_delivery_authority.py`
   - stale fixture aligned to the already-authoritative explicit `client_surface_safety` contract; no product behavior changed.

## Exact-head validation

```text
candidate_head=2f70796037999a2cc543ecfe2df477ca02a8e324
email_equity_parity_run=32109238595 result=SUCCESS
product_boundary_run=32109238376 result=SUCCESS
donor_parity_run=32109238441 result=SUCCESS
canonical_report_artifacts_changed=false
portfolio_mutation=false
broker_execution=false
resend_executed=false
```

## Operational runbook remaining
1. Perform independent blind-first `governance_release_assurance` on PR #106 exact head `2f70796037999a2cc543ecfe2df477ca02a8e324` against base `d9b4ecac4f49417fd7430b01303d1c3425b7074a`.
2. Merge only an unchanged PASSed head.
3. Reconcile project control state and stable decision/defect history after merge.
4. Do not resend the already-delivered report without a separate governed send action.

## Acceptance status
- mail-safe equity curve representation: PASS in CI;
- NL/EN MIME parity tests: PASS;
- product boundary: PASS;
- donor parity/full-package regressions: PASS;
- canonical report bytes changed: NO;
- independent exact-head assurance: PENDING;
- merge: PENDING;
- corrected resend: NOT AUTHORIZED / NOT EXECUTED.
