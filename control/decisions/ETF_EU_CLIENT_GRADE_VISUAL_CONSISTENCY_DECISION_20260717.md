# ETF EU Client-Grade Visual Consistency Decision — 2026-07-17

## Decision

A successful workflow and a green machine-validation artifact are necessary but not sufficient for accepting or delivering a Weekly ETF EU client report.

Every client-grade Dutch/English package must also pass a separate complete visual review with explicit evidence.

## Current trigger

Preview run `20260717_114500` passed:

- focused regression tests;
- current UCITS pricing collection;
- macro and valuation refresh;
- funded-aware state generation;
- Dutch and English HTML/PDF rendering;
- strict funded-state and semantic ISIN validation.

The package was nevertheless rejected because the rendered surface contained date-label overlap, poor funded-table wrapping and a Dutch localization defect.

## Four-layer placement

### 1. Decision framework

Visual review does not decide portfolio allocation. It decides whether the already-produced client surface accurately and professionally communicates the authorized model state.

### 2. Input/state contract

Portfolio quantities, cash, NAV, exact ISINs, pricing dates and valuation history remain sourced from the canonical EU state and evidence artifacts. Visual review may not rewrite those facts.

### 3. Output contract

Client-grade acceptance requires all of the following:

```text
machine_validation_passed=true
visual_review_passed=true
content_consistency_passed=true
client_grade_preview_accepted=true
blockers=[]
```

Identifiers and numeric values must not be broken into misleading fragments. Charts must not contain overlapping labels. Dutch client surfaces must not retain English operational comments.

### 4. Operational runbook

```text
generate Dutch and English HTML/PDF
→ run strict machine gates
→ render every page
→ inspect all Dutch and English pages
→ persist visual-review artifact
→ accept or reject the immutable preview identity
→ open delivery only after separate explicit authority
```

## Upstream donor decision

The EU equity-curve implementation continues to adapt the mature SVG approach from `market-predictions/weekly-etf`.

The EU version intentionally diverges by adding a minimum-spacing rule for representative x-axis ticks and edge-aligned endpoint labels. The donor renderer uses fixed representative indices and does not prevent adjacent-date collisions.

## Stable visual rules

1. Preserve the first and last equity-curve dates.
2. Suppress intermediate date ticks that cannot maintain the minimum visual spacing.
3. Keep funded ticker, ISIN, quantity, price, pricing date, market value and weights unbroken where practical.
4. Use fixed column contracts for dense funded and pricing tables.
5. Keep the funded ISIN identity strip visible and extractable in HTML and PDF.
6. Keep Dutch client-facing operational comments in Dutch.
7. Do not repair a rejected immutable report in place; generate a new run ID and suffix.

## Authority boundaries

```text
portfolio_mutation=false
real_broker_execution=false
transport_attempted=false
send_executed=false
production_delivery_authority=false
```

A visual-review pass is not delivery authority. Delivery requires a separate guarded instruction and real transport plus receipt evidence.
