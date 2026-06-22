# ETF EU cockpit PDF premium surface improvement decision notes — WP15I

## 1. Package status

```text
work_package=WP15I
source_work_package=WP15H
status=completed
decision=targeted_copy_governance_refinement_before_delivery_preflight
keep_as_current_review_artifact=true
targeted_improvement_needed=true
delivery_preflight_allowed=false
selected_next_package=WP15J
selected_next_package_title=ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery
```

WP15I is a decision/planning package only. It does not create a new PDF, does not render a PDF, does not change the premium renderer, does not replace the premium PDF, and does not enable delivery.

## 2. Source files inspected

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_closeout_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
tools/validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py
tests/test_etf_eu_cockpit_pdf_premium_surface_review_checkpoint.py
```

## 3. Decision question 1 — Should the premium PDF remain the current stable review artifact?

```text
keep_as_current_review_artifact=true
```

Yes. The existing premium PDF should remain the current stable review artifact.

Reasons:

- WP15H already records it as acceptable for the review checkpoint.
- It preserves the authority boundaries: no delivery, no portfolio mutation, no candidate promotion, no funding authority, and no valuation-grade authority.
- It is materially better than the MVP and layout surfaces because it uses five logical cockpit pages, Dutch-first executive framing, repeated boundary markers, candidate/evidence cards, UCITS/proxy separation, and an action/validation checklist.
- It is still correctly positioned as proof-of-concept / review-only.

## 4. Decision question 2 — Is a targeted improvement iteration needed before delivery-preflight?

```text
targeted_improvement_needed=true
```

Yes. A narrow improvement iteration is needed before any delivery-preflight planning.

Reason:

The premium PDF is strong enough as a review artifact, but it still exposes raw machine-checkable marker strings and developer-like evidence labels in the visible client surface. Those markers are useful for deterministic validators, but they are not clean enough for final client-facing delivery-preflight.

Targeted improvement scope:

- client-facing copy refinement;
- visible marker/debug language reduction;
- clearer client-language badges while preserving raw validator markers;
- sharper Dutch executive summary;
- compact explanation of review evidence versus pricing evidence versus valuation-grade evidence;
- preservation of machine-checkable raw markers for validators.

This should be a targeted copy/governance refinement plan, not a broad redesign.

## 5. Decision question 3 — Should delivery-preflight remain blocked?

```text
delivery_preflight_allowed=false
delivery_authorization_decision=remain_blocked
```

Yes. Delivery-preflight remains blocked.

Reasons:

- No delivery receipt exists.
- No production manifest exists.
- No outbound path has been enabled.
- No client distribution has been claimed.
- No valuation-grade evidence exists.
- No funding authority exists.
- No live market refresh or pricing-evidence refresh authority exists.
- No separate approved receipt/manifest authority package exists.

## 6. Rejected scopes for WP15I

WP15I explicitly rejects these scopes:

```text
new_pdf_created=false
renderer_changed=false
premium_pdf_replaced=false
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
live_data_fetch_performed=false
recommendation_logic_changed=false
outbound_path_enabled=false
receipt_artifact_created=false
production_manifest_created=false
client_distribution_claimed=false
```

Rejected work:

- broad renderer redesign;
- PDF rendering or replacement;
- delivery-preflight enablement;
- recipient, SMTP, secret, or outbound changes;
- portfolio mutation;
- candidate promotion;
- funding or valuation authority;
- live data fetch;
- recommendation logic changes.

## 7. Selected next package

```text
WP15J — ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery
```

Purpose:

```text
Plan a narrow refinement that improves client-facing copy and badge language while preserving validator markers, authority boundaries and no-delivery status.
```

WP15J should remain planning-only unless a separate instruction explicitly authorizes implementation.

## 8. Boundary confirmation

```text
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
live_data_fetch_performed=false
recommendation_logic_changed=false
renderer_changed=false
new_pdf_created=false
premium_pdf_replaced=false
outbound_path_enabled=false
receipt_artifact_created=false
production_manifest_created=false
client_distribution_claimed=false
delivery_authorization_decision=remain_blocked
```
