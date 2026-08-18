# ETF EU Email Equity Parity — Issue 105

## Identity

```text
workpackage_id=ETF-EU-EMAIL-EQUITY-PARITY-105
claim_id=ETF-EU-EMAIL-EQUITY-PARITY-105
issue=105
repository=market-predictions/weekly-etf-eu
branch=agent/etf-eu-email-equity-parity-105
base_main_sha=d9b4ecac4f49417fd7430b01303d1c3425b7074a
owner_role=implementation_operations
status=ACTIVE
opened_at=2026-08-18T06:52:23Z
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
- canonical NL/EN HTML remains the source representation;
- canonical NL/EN PDF remains unchanged;
- the equity curve is identified by `class="equity-curve-svg"` in the canonical HTML;
- no portfolio, pricing, allocation or broker state may be changed.

## Output contract
For HTML email delivery when an equity curve is present:
- the email HTML must replace the inline curve SVG with one `<img src="cid:...">` representation;
- the message must contain the matching `image/png` MIME-related part;
- the CID must resolve exactly once;
- the canonical HTML/PDF files are not rewritten;
- missing/failed conversion blocks message construction.

## Operational runbook
1. Add deterministic SVG→PNG conversion to the controlled sender using a pinned CairoSVG runtime dependency.
2. Add MIME-related/CID embedding and explicit parity assertions.
3. Add NL/EN regression tests that inspect the constructed MIME structure.
4. Add a dedicated CI gate for the repair branch/PR.
5. Open PR, inspect exact diff and CI evidence, then obtain any required independent assurance before merge.
6. Do not resend the already-delivered report without a separate governed send action.

## Acceptance criteria
- PDF-equity-curve / email-equity-curve parity is machine-gated;
- inline curve SVG is not the email transport representation;
- NL and EN tests pass;
- no canonical report artifact bytes or portfolio state are changed;
- future controlled transport fails closed if mail-safe chart materialization fails.
