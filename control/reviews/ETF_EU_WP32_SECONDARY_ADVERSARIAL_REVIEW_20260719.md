# ETF EU WP32 — Secondary adversarial review

Date: 2026-07-19
Role: independent critical review pass
Mutation authority: none
Final status: passed after two iterations

## Review mandate

Challenge the primary implementation from the perspectives of client comprehension, factual authority, EU/UCITS identity, duplication, email degradation, PDF pagination, accessibility and operational isolation.

## Challenges completed

1. Every visible portfolio figure was reconciled to the normalized EU state.
2. The page describes repository-model activity and does not imply a real brokerage transaction or approved later tranche.
3. Remaining cash is explicitly described as capacity rather than automatic deployment authority.
4. EUNA is described as a stabiliser rather than guaranteed protection; VWCE/SXR8 overlap remains a discipline issue.
5. Return precision was increased from `+0.0%` to `+0.02%`, and max drawdown now discloses the three-point valuation history.
6. Successful injection suppresses the compact investor summary strip while retaining section 1 as detailed rationale.
7. The order cockpit -> investor report -> analyst report is preserved in Dutch and English.
8. The email-safe page uses inline presentation styles, and duplicate summary content remains hidden without head CSS.
9. All seven pages in each language were inspected at 200 dpi.
10. Protected portfolio, ledger, recommendation, state and classic-report inputs remained unchanged.

## Resolved findings

- The first email-safe design depended on head CSS for summary suppression. This was replaced by inline `display:none!important`.
- One-decimal percentage formatting masked the actual small positive return. The cockpit now shows `+0.02%` / `+0,02%`.
- The initial max-drawdown label did not disclose the short history. It now states `3 valuation points` / `3 waarderingspunten`.
- A4 page density, document transitions and section-1 duplication were inspected and accepted. Section 1 adds detailed decision rationale rather than repeating the compact metric surface.

## Evidence

```text
github_run_id=29666911258
machine_validation_passed=true
protected_inputs_unchanged=true
visual_review_artifact=output/cockpit_preview/etf_eu_wp32_visual_review_20260719.json
NL_pages_reviewed=7
EN_pages_reviewed=7
blockers=0
```

## Gate

```text
secondary_review_passed=true
rendered_evidence_reviewed=true
production_promotion_recommended=true
production_enablement_granted=false
```

Production enablement remains a separate WP33 decision and requires an exact-current replay with rollback evidence.