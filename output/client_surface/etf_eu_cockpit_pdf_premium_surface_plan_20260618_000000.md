# ETF EU cockpit PDF premium surface plan — WP15E

## 1. Planning status

```text
work_package=WP15E
status=completed
planning_only=true
new_pdf_created=false
renderer_changed=false
source_work_package=WP15D
selected_next_package=WP15F
selected_next_package_title=ETF EU cockpit PDF premium surface implementation, no delivery
```

WP15E defines the target premium client-grade cockpit PDF surface. It does not implement a new renderer, does not render a new PDF, and does not enable an outbound report path.

## 2. Source artifacts inspected

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_mvp_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_mvp_review_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_mvp_layout_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_mvp_layout_closeout_notes_20260618_000000.md
tools/render_etf_eu_cockpit_pdf_mvp.py
tools/render_etf_eu_cockpit_pdf_mvp_layout.py
tools/validate_etf_eu_cockpit_pdf_mvp.py
tools/validate_etf_eu_cockpit_pdf_mvp_layout.py
```

## 3. What WP15A proved

WP15A proved that the ETF EU cockpit can produce a real committed PDF artifact from validated proof-of-concept inputs.

Key proof points:

- A deterministic PDF MVP renderer exists.
- The PDF path is stable and committed.
- The original PDF starts with a valid PDF header.
- The PDF contains the required proof-of-concept and review-only boundary markers.
- The output can be validated without enabling report distribution.

## 4. What WP15C improved

WP15C improved readability without replacing the original WP15A PDF.

Confirmed improvements:

- The original WP15A PDF remained preserved.
- A separate improved layout PDF was created.
- A four-page structure was introduced.
- Dutch-first cockpit hierarchy was improved.
- Candidate facts were grouped into cleaner PDF-readable blocks.
- Pricing boundary was made more visible.
- Research proxy separation was made clearer.
- Blocked authority markers remained visible.

## 5. Remaining gap to premium client-grade

The current layout PDF is a useful MVP, but not yet the final premium client surface.

Remaining gaps:

- It uses deterministic low-level PDF writing instead of a proper design system.
- Visual polish is functional rather than client-grade.
- Tables/cards are still text-driven and need stronger spacing, alignment and hierarchy.
- Page rhythm and typography need a consistent visual language.
- Dutch-first conclusions need to be shorter, more executive and more visually prominent.
- Boundary badges should become visually distinct and consistently placed.
- The output still lacks production-grade report branding and layout primitives.

## 6. Target premium cockpit structure

The future premium PDF should use this structure.

### Page 1 — Executive cockpit cover

- Portfolio/report title.
- Date/run metadata.
- Proof-of-concept / review-only badge while delivery remains blocked.
- Clear boundary badge block.
- One Dutch-first executive conclusion.
- Compact summary: what can be used, what is blocked, and what needs verification.

### Page 2 — Decision cockpit

- Current review-only usable baseline.
- Candidate lanes.
- Blocked/incomplete lanes.
- Clear no valuation-grade authority and no funding authority labels.

### Page 3 — UCITS evidence cockpit

- ISIN-first identity.
- Exchange line.
- Pricing-symbol evidence.
- UCITS / PRIIPs / KID / trading line status placeholders.
- Source evidence status.
- Next verification action.

### Page 4 — Research proxy separation

- U.S. proxy versus EU/UCITS candidate.
- Allowed proxy use.
- Blocked use.
- Pricing authority status.
- Funding authority status.

### Page 5 — Action and validation checklist

- What is review-only usable.
- What must stay blocked.
- What must be verified before promotion.
- What must be true before delivery can ever be enabled.

## 7. Visual hierarchy requirements

The premium PDF surface should use:

- Clear page titles.
- Compact summary blocks.
- Whitespace between sections.
- Strong section hierarchy.
- Consistent badge/status language.
- Readable tables or card-like candidate blocks.
- Dutch-first wording for client-facing conclusions.
- English only where needed for technical traceability.
- Explicit separation between investable UCITS candidates and U.S. proxies.

## 8. Dutch-first client reading flow

The client-facing flow should be Dutch-first and decision-oriented:

1. Start with a short Dutch executive conclusion.
2. Show what is currently usable only as review evidence.
3. Show what is blocked or incomplete.
4. Show what must be verified before any promotion or funding decision.
5. Keep technical English labels only where they support traceability.

Preferred reader language:

- bruikbaar als reviewbewijs
- nog niet veilig voor prijsbewijs
- geblokkeerd tot beleidsbesluit
- geen valuation-grade autoriteit
- geen funding authority
- researchproxy, geen EU-holding

## 9. Table and data presentation requirements

Future implementation should avoid dense markdown-style tables.

Use one of these PDF-native patterns:

- card-like candidate blocks for each UCITS candidate;
- compact two-column fact rows for ISIN, pricing line, status and action;
- small status badge rows for evidence, block reason and next verification action;
- summary matrix only when columns remain readable at PDF width.

Required table/card facts:

- candidate name;
- ISIN-first identity;
- exchange line / pricing symbol evidence;
- research proxy;
- pricing evidence status;
- investability / policy status;
- next verification action;
- authority boundary state.

## 10. Boundary/authority display requirements

Boundary information must be visible and repeated where decisions could be misread.

Required markers:

```text
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
```

The premium surface should show these as clear badges or callouts, not only as technical text.

## 11. Research proxy separation requirements

The future surface must keep U.S. research proxies visually separate from EU/UCITS candidates.

Required distinction:

- U.S. proxy: benchmark or research context only.
- EU/UCITS candidate: potential investable instrument only after identity, UCITS status, PRIIPs/KID, trading line and pricing evidence are validated.
- Proxy symbols must never be shown as EU holdings, EU pricing lines or funding sources.

Required proxy rows:

```text
SPY=research_proxy_only
SMH=research_proxy_only_and_ambiguous_as_pricing_symbol
GLD=research_proxy_only_not_eu_holding
PAVE=research_proxy_only_not_eu_holding
```

## 12. PDF renderer implications

The future implementation package should not simply add more text to the current renderer.

Recommended implementation direction:

- Keep deterministic generation.
- Preserve pure-Python rendering if dependency-light output remains sufficient.
- Introduce reusable layout primitives: page title, badge block, summary card, candidate card, evidence table, footer.
- Keep PDF text markers machine-checkable for validators.
- Preserve original WP15A and WP15C artifacts as historical evidence.
- Avoid adding live data, external network calls, browser exports or outbound report actions.

## 13. Validation requirements for the future implementation package

The future implementation validator should confirm:

- the premium PDF exists;
- the premium PDF starts with %PDF;
- the premium PDF contains all required boundary markers;
- the premium PDF contains the five-page target structure markers;
- the PDF contains Dutch-first executive conclusion text;
- the PDF contains ISIN-first candidate identity fields;
- the PDF contains explicit research proxy separation markers;
- the original WP15A PDF remains preserved;
- the WP15C layout PDF remains preserved;
- no distribution path, pricing evidence, recommendation logic or authority boundary changed.

## 14. Non-goals

WP15E does not:

- create a new PDF;
- render a new PDF;
- redesign the renderer;
- edit the WP15A original PDF;
- edit the WP15C layout PDF;
- enable an outbound report path;
- create a report receipt artifact;
- create or modify recipient configuration;
- create or modify credential configuration;
- fetch live data;
- update pricing evidence;
- change ETF recommendation logic;
- mutate portfolio state;
- promote candidates;
- create funding authority;
- create valuation-grade authority;
- create another review-feedback package;
- reopen WP14V.

## 15. Recommended next package

```text
selected_next_package=WP15F
selected_next_package_title=ETF EU cockpit PDF premium surface implementation, no delivery
```

WP15F should implement the planned premium surface while preserving all no-delivery and no-authority boundaries.

## Four-layer preservation

### Decision framework

The premium surface may make decisions easier to read, but it must not create a new investment decision or promotion authority.

### Input/state contract

The premium surface must continue to use validated, ISIN-first UCITS identity and explicitly distinguish review-only pricing evidence from valuation-grade evidence.

### Output contract

The premium surface must provide a Dutch-first, client-readable PDF cockpit that separates investable UCITS candidates from U.S. research proxies.

### Operational runbook

Future implementation must remain deterministic, testable and validator-backed, with no delivery enabled until a separate explicit delivery receipt/manifest authority exists.
