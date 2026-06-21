# ETF EU cockpit PDF MVP layout notes — WP15C

## Scope

```text
work_package=WP15C
source_pdf=output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
layout_pdf=output/client_surface/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.pdf
selected_next_package=WP15D
selected_next_package_title=ETF EU cockpit PDF MVP layout closeout, no delivery
```

WP15C is a layout/readability iteration only. It does not change pricing evidence, recommendation logic, delivery behavior or authority boundaries.

## Source files inspected

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_mvp_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_mvp_review_notes_20260618_000000.md
tools/render_etf_eu_cockpit_pdf_mvp.py
tools/validate_etf_eu_cockpit_pdf_mvp.py
tests/test_etf_eu_cockpit_pdf_mvp.py
output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md
output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md
```

## Layout/readability improvements

- Preserves the original WP15A PDF as historical MVP evidence.
- Creates a separate layout PDF artifact instead of replacing the first MVP.
- Adds a clearer four-page structure: cover, Dutch-first universe, pricing boundary, proxy separation.
- Uses larger section headings and clearer hierarchy.
- Presents candidates as grouped PDF-readable blocks instead of dense markdown/table text.
- Makes the blocked authority boundary visible on the cover and final page.
- Keeps research proxies explicitly separated from EU holdings and EU pricing authority.

## Known limitations after WP15C

- This remains a proof-of-concept PDF surface.
- The renderer is still a deterministic pure-Python MVP renderer, not a full design system.
- Visual styling is improved but still not final premium production layout.
- This package does not enable report delivery.

## Boundary confirmation

```text
proof_of_concept_pdf_mvp=true
delivery_authorization_decision=remain_blocked
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
no_email_action_occurred=true
portfolio_state_modified=false
```

## Next package

```text
WP15D — ETF EU cockpit PDF MVP layout closeout, no delivery
```

WP15D should close out the layout iteration after validation. It should not implement delivery.
