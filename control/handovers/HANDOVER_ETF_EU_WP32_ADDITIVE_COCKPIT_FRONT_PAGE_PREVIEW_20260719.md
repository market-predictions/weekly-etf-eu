# Handover — ETF-EU-WP32 additive cockpit front-page preview

Date: 2026-07-19
Branch: `feature/etf-eu-wp32-additive-cockpit-preview`
Status: implementation and review complete

## Delivered

- EU/UCITS state-derived cockpit front-page renderer;
- separate inline/table email-safe surface;
- explicit feature gate `MRKT_RPRTS_ETF_EU_COCKPIT_FRONT_PAGE`;
- fail-closed classic fallback;
- one-page additive injection before the existing investor and analyst reports;
- inline suppression of the compact investor summary strip after successful injection;
- machine validator and regression tests;
- isolated GitHub validation workflow and main-branch validation bridge;
- complete bilingual HTML/PDF/email preview package;
- independent adversarial review and visual evidence.

## Donor adaptation

Reused the donor's additive front-page, runtime-state, email-safe rendering, feature-gate and rollback concepts. EU-specific authority remains ISIN-first, UCITS-first, Dutch-primary and EUR-based. No U.S. portfolio state or investability assumption was ported.

## Final evidence

```text
validation_run=29666911258
regression_tests_passed=true
machine_validation_passed=true
protected_inputs_unchanged=true
NL_pdf_pages=7
EN_pdf_pages=7
classic_page_count=6
page_delta=1
classic_sections_preserved=15
primary_visual_review_passed=true
secondary_adversarial_review_passed=true
blockers=0
```

Evidence files:

```text
output/cockpit_preview/etf_eu_cockpit_front_page_validation_20260719.json
output/cockpit_preview/etf_eu_wp32_validation_receipt_20260719.json
output/cockpit_preview/etf_eu_wp32_visual_review_20260719.json
control/reviews/ETF_EU_WP32_SECONDARY_ADVERSARIAL_REVIEW_20260719.md
```

## Review-driven corrections

1. summary suppression changed from head-CSS dependence to inline `display:none!important`;
2. small positive return changed from rounded `+0.0%` to `+0.02%`;
3. max-drawdown context now states the three-point valuation-history depth.

## Authority boundary

```text
production_enablement=false
production_workflow_changed=false
current_client_package_changed=false
portfolio_state_changed=false
trade_ledger_changed=false
pricing_state_changed=false
report_sent=false
```

## Next package

```text
ETF-EU-WP33_COCKPIT_FRONT_PAGE_PRODUCTION_ENABLEMENT
```

WP33 must perform an exact-current, non-delivery replay, prove the one-switch rollback and only then decide whether to enable the EU feature flag in the production generation path. A later actual report send remains separately governed.

## Separate unresolved governance item

WP31 confirmed the prior mailbox receipt independently, but connector privacy controls prevented persistence of mailbox-derived receipt metadata. The existing report must not be resent. Repository closeout remains fail-closed until a permitted redaction-safe persistence route exists.