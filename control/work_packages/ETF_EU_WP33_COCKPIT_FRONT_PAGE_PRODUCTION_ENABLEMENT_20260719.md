# ETF-EU-WP33 — Cockpit front-page production enablement

Date: 2026-07-19
Status: claimed / in progress
Branch: `feature/etf-eu-wp33-cockpit-production-enablement`

## Purpose

Promote the merged WP32 additive cockpit capability into the Weekly ETF EU routine package-build path after an exact-current, non-delivery replay.

## Donor pattern

Adapt the donor's separate production-enablement phase:

- implementation already validated before enablement;
- exact-current replay through the real output path;
- explicit feature flag;
- one-switch rollback;
- classic report fallback;
- no state, pricing or allocation authority change;
- future transport remains separately governed.

## Layers

```text
decision framework=unchanged
input/state contract=current normalized EU state
output contract=optional additive cockpit page
operational runbook=exact-current non-delivery replay and rollback proof
```

## Planned changes

1. Integrate the feature-gated cockpit injector into `tools/build_etf_eu_routine_report_package_v2.py`.
2. Keep missing or disabled feature state on the current two-part report.
3. Add production-path metadata to package, ready and routine manifests.
4. Build an exact-current replay tool that writes only to `output/cockpit_enablement_preview/`.
5. Validate disabled and enabled outputs against the accepted 2026-07-17 package.
6. Verify one additional page, unchanged fifteen-section body and inline email compatibility.
7. Recheck protected state and control hashes.
8. Require primary and independent adversarial review.
9. Record a separate enablement decision only after every gate passes.

## Acceptance

```text
exact_current_state_used=true
non_delivery_replay=true
disabled_classic_contract_passed=true
enabled_page_delta=1
cockpit_investor_analyst_order_passed=true
classic_sections_preserved=15
email_safe_surface_passed=true
protected_inputs_unchanged=true
primary_review_passed=true
secondary_review_passed=true
blockers=[]
```

## Boundaries

```text
accepted_20260717_package_unchanged=true
portfolio_state_unchanged=true
trade_ledger_unchanged=true
pricing_state_unchanged=true
allocation_authority_unchanged=true
real_broker_execution=false
external_transport=false
```
