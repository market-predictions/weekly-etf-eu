# ETF EU Email Equity Donor-Parity Decision — 2026-08-18

## Decision

Weekly ETF EU uses the established Weekly ETF donor delivery architecture for portfolio equity-curve representation across client surfaces.

The graph is materialized and validated before SMTP transport. Final standalone HTML embeds the approved PNG bytes as a `data:image/png;base64,...` source. The final PDF is rendered from that same final HTML. Controlled email transport does not redraw or rasterize the graph; it only translates the already-approved PNG bytes to `cid:equitycurve` and attaches those identical bytes as one inline `image/png` related part.

## Authority

This decision was integrated through:

```text
issue=105
pull_request=106
trusted_base=d9b4ecac4f49417fd7430b01303d1c3425b7074a
assured_candidate=57fef69626951f2a33bc63ced25253bcc4e84df0
independent_assurance_issue=108
independent_assurance_verdict=PASS
merge_commit=1fb7168f7ba433e138503c68aa9447c5f7ebbc65
```

Donor design precedent:

```text
market-predictions/weekly-etf@3ffff5e6104fcc2b72ce6553718a59be2905d3af
runtime/equity_curve_png_contract.py
runtime/standalone_html_equity_embed.py
control/decisions/REPORT_FRESHNESS_AND_STANDALONE_HTML_EQUITY_DECISION_20260716.md
```

## Stable contract

When `equity_curve.show_chart=true`:

1. deterministic PNG rendering occurs before guarded email transport;
2. final standalone HTML contains exactly one embedded PNG equity image;
3. final PDF is generated from that final HTML surface;
4. controlled email HTML contains exactly one `cid:equitycurve` reference;
5. MIME contains exactly one matching inline `image/png` related part;
6. MIME PNG bytes equal the PNG bytes embedded in the approved HTML;
7. residual SVG, missing/ambiguous embedded PNG, malformed base64 or non-PNG payload fails closed.

When the report state does not require a graph, no graph is invented.

## Boundaries

This decision does not create or expand:

```text
portfolio_mutation_authority=false
pricing_authority=false
allocation_authority=false
trade_ledger_mutation_authority=false
broker_execution_authority=false
email_delivery_authority=false
historical_report_resend_authority=false
```

Guarded-delivery authority, artifact-hash binding, explicit send confirmations and recipient-side receipt/closeout remain separate gates.

## Consequence

Future Weekly ETF EU report cycles must use this donor-aligned graph contract so the PDF, standalone HTML and email surfaces remain graph-equivalent without rendering inside the SMTP layer.
