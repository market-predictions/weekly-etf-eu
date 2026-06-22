# ETF EU cockpit PDF premium surface improvement decision notes — ETF-EU-WP15I-RECONCILE

## 1. Decision status

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15I-RECONCILE
legacy_work_package_id=WP15I
source_work_package=WP15H
status=completed
improvement_decision_created=true
improvement_decision=create_targeted_improvement_package
decision=targeted_copy_governance_refinement_before_delivery_preflight
keep_as_current_review_artifact=true
targeted_improvement_needed=true
targeted_improvement_package_required=true
targeted_improvement_package=ETF-EU-WP15J
delivery_preflight_allowed=false
selected_next_package=ETF-EU-WP15J
selected_next_package_title=ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery
```

ETF-EU-WP15I-RECONCILE aligns the existing WP15I decision with the coordinator instruction. The existing premium PDF remains the current stable review artifact, but a narrow copy/governance refinement package is required before delivery-preflight planning.

This reconcile package does not create a new PDF, does not render a PDF, does not change the premium renderer, does not replace the premium PDF, and does not enable delivery.

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
tools/validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py
tests/test_etf_eu_cockpit_pdf_premium_surface_improvement_decision.py
```

## 3. Reconciled decision

Previous main decision before reconcile:

```text
improvement_decision=keep_current_premium_surface
targeted_improvement_package_required=false
targeted_improvement_package=null
```

Reconciled decision:

```text
improvement_decision=create_targeted_improvement_package
targeted_improvement_package_required=true
targeted_improvement_package=ETF-EU-WP15J
```

Rationale:

WP15H correctly found the premium PDF acceptable for review-checkpoint use. That does not mean it is clean enough for delivery-preflight. The PDF still exposes raw machine-checkable marker strings and developer-like evidence language in the visible client surface. Those markers are useful for deterministic validation, but they should be translated into cleaner client-facing copy and badges before any delivery-preflight package.

## 4. Decision question 1 — Should the premium PDF remain the current stable review artifact?

```text
keep_as_current_review_artifact=true
```

Yes. The current premium PDF remains the stable review artifact because it is already validated, preserves authority boundaries, is materially better than the MVP/layout surfaces, and remains clearly proof-of-concept / review-only.

## 5. Decision question 2 — Is targeted improvement needed before delivery-preflight?

```text
targeted_improvement_needed=true
targeted_improvement_package_required=true
```

Yes. A targeted copy/governance refinement is required before delivery-preflight.

Recommended improvement scope:

- client-facing copy refinement;
- visible marker/debug language reduction;
- clearer client-language badges while preserving raw validator markers;
- sharper Dutch executive summary;
- compact explanation of review evidence versus pricing evidence versus valuation-grade evidence;
- preservation of machine-checkable raw markers for validators.

This is not a broad renderer redesign and not a delivery package.

## 6. Decision question 3 — Should delivery-preflight remain blocked?

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

## 7. Rejected scopes for ETF-EU-WP15I-RECONCILE

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
pricing_evidence_changed=false
recommendation_logic_changed=false
outbound_path_enabled=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
```

Rejected work:

- new PDF creation;
- renderer change;
- premium PDF replacement;
- delivery-preflight enablement;
- recipient, SMTP, secret, or outbound changes;
- portfolio mutation;
- candidate promotion;
- funding or valuation authority;
- live data fetch;
- recommendation logic changes.

## 8. Selected next package

```text
ETF-EU-WP15J — ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery
```

Purpose:

```text
Plan a narrow refinement that improves client-facing copy and badge language while preserving validator markers, authority boundaries and no-delivery status.
```

ETF-EU-WP15J should remain planning-only unless separately authorized.

## 9. Boundary confirmation

```text
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
outbound_path_enabled=false
live_data_fetch_performed=false
pricing_evidence_changed=false
recommendation_logic_changed=false
new_pdf_created=false
renderer_changed=false
premium_pdf_replaced=false
client_distribution_claimed=false
receipt_artifact_created=false
production_manifest_created=false
```
