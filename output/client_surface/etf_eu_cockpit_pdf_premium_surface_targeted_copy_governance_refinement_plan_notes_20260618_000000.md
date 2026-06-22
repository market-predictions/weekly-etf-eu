# ETF EU cockpit PDF premium surface targeted copy/governance refinement plan notes — ETF-EU-WP15J

## 1. Plan status

```text
repository=market-predictions/weekly-etf-eu
work_package_id=ETF-EU-WP15J
legacy_work_package_id=WP15J
source_work_package=ETF-EU-WP15I-RECONCILE
status=completed
targeted_refinement_plan_created=true
targeted_refinement_plan_decision=plan_future_copy_governance_refinement
implementation_in_this_package=false
selected_next_package=ETF-EU-WP15K
```

ETF-EU-WP15J creates a planning-only package for a narrow future copy/governance refinement. It does not create or render a PDF and does not change the premium renderer.

## 2. Source files inspected

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_improvement_decision_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_20260618_000000.json
output/client_surface/etf_eu_cockpit_pdf_premium_surface_review_checkpoint_notes_20260618_000000.md
output/client_surface/etf_eu_cockpit_pdf_premium_surface_plan_20260618_000000.md
```

## 3. Premium PDF path and commit

```text
premium_pdf_path=output/client_surface/weekly_etf_eu_cockpit_premium_surface_20260618_000000.pdf
premium_pdf_commit=fb7751026a70db355385946ee3882c68f9ec0e71
premium_pdf_preserved=true
```

## 4. Reconciled WP15I authority

```text
improvement_decision=create_targeted_improvement_package
decision=targeted_copy_governance_refinement_before_delivery_preflight
keep_as_current_review_artifact=true
targeted_improvement_needed=true
targeted_improvement_package_required=true
targeted_improvement_package=ETF-EU-WP15J
delivery_preflight_allowed=false
delivery_authorization_decision=remain_blocked
```

## 5. Reason targeted refinement is needed

The current premium PDF remains the stable review artifact, but before any delivery-preflight decision the visible client surface needs a narrow copy/governance refinement.

The concern is not analytical content or renderer structure. The concern is the visible presentation layer:

- raw machine-checkable marker strings are useful for validators but should be reduced or translated in client-facing language;
- developer-like evidence language should be made clearer for a premium client surface;
- governance badges should remain explicit but more readable;
- the difference between review evidence, pricing evidence, valuation-grade evidence and delivery authority should be more compact and understandable.

## 6. Current premium PDF status

```text
current_premium_surface_status=stable_current_review_artifact
proof_of_concept_pdf_mvp=true
production_delivery=false
```

The current premium PDF remains preserved as the stable review artifact. It is not replaced by this package.

## 7. Refinement scope

```text
refinement_scope=client-facing copy refinement
refinement_scope=visible marker/debug language reduction
refinement_scope=client-language badge refinement while preserving raw validator markers
refinement_scope=sharper Dutch executive summary
refinement_scope=compact explanation of review evidence versus pricing evidence versus valuation-grade evidence
refinement_scope=clearer no-delivery and no-authority wording
refinement_scope=preserve UCITS/proxy separation language
```

## 8. Explicit out-of-scope items

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

Out of scope:

- new PDF creation in ETF-EU-WP15J;
- PDF rendering in ETF-EU-WP15J;
- premium renderer change in ETF-EU-WP15J;
- premium PDF replacement in ETF-EU-WP15J;
- delivery enablement;
- receipt creation;
- production manifest creation;
- client distribution claim;
- portfolio mutation;
- candidate promotion;
- funding authority;
- valuation-grade authority;
- live data fetch;
- pricing evidence update;
- recommendation logic change.

## 9. Client-facing copy refinement plan

The future implementation package should refine copy only where it improves client readability without changing investment logic.

Recommended future copy changes:

- convert developer-facing validation statements into concise client-facing explanations;
- keep the proof-of-concept and no-delivery status visible;
- clarify that the report is a controlled review artifact, not a sent production report;
- make the wording around incomplete lanes and blocked authority more natural in Dutch;
- avoid hiding any governance boundary.

## 10. Governance badge/language refinement plan

The future implementation package should preserve all governance facts while improving visual/client language.

Recommended future badge changes:

- retain no-delivery and no-authority badges;
- use clearer labels for production_delivery=false, valuation_grade=false, funding_authority=false and delivery_authorization_decision=remain_blocked;
- avoid raw boolean clutter in the visible client layer where a human-readable label can carry the same meaning;
- keep machine-checkable markers available for validators outside or alongside the visible client copy.

## 11. Validator marker preservation plan

Validator markers must remain deterministic and machine-checkable.

The future implementation package should not remove raw markers from the artifact contract. It may reduce visible debug-like language if the validator can still verify the same facts through structured metadata, hidden data blocks, deterministic comments or non-client-facing evidence sections.

## 12. Dutch executive summary refinement plan

The Dutch executive summary should become sharper and more explicitly client-facing.

Recommended future changes:

- state the main conclusion first;
- explain why no delivery/preflight authority exists yet;
- distinguish review readiness from delivery readiness;
- avoid technical validator language in the executive conclusion;
- keep UCITS/proxy separation visible but compact.

## 13. UCITS/proxy separation preservation plan

The future implementation package must preserve the UCITS/proxy authority model.

Required preserved distinctions:

- UCITS ETF candidates are investable review targets only after EU identity and investability checks;
- U.S. ETFs are research proxies only;
- proxy symbols must not become EU holdings;
- proxy symbols must not become pricing authority;
- proxy symbols must not create funding or valuation-grade authority.

## 14. Boundary confirmation

```text
production_delivery=false
portfolio_mutation=false
candidate_promotion=false
funding_authority=false
valuation_grade=false
delivery_authorization_decision=remain_blocked
delivery_preflight_allowed=false
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

## 15. Known remaining limitations

- The premium PDF is still proof-of-concept / review-only.
- It is not production delivery.
- It has not been sent to a client.
- It does not include live market refresh.
- It does not create valuation-grade authority.
- It does not create funding authority.
- It does not create candidate promotion authority.
- Delivery-preflight remains blocked.
- A delivery receipt still does not exist.
- A production manifest still does not exist.
- The actual refinement implementation is not done in ETF-EU-WP15J.

## 16. Recommended next package

```text
ETF-EU-WP15K — ETF EU cockpit PDF premium surface targeted copy/governance refinement implementation, no delivery
```

ETF-EU-WP15K may implement the narrow copy/governance refinement, but must remain no-delivery unless a later explicit package creates delivery authority.
