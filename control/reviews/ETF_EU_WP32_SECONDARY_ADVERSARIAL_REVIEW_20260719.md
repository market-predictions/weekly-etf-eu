# ETF EU WP32 — Secondary adversarial review

Date: 2026-07-19
Role: independent critical review pass
Mutation authority: none
Initial status: pending rendered evidence

## Review mandate

Challenge the primary implementation from the perspectives of client comprehension, factual authority, EU/UCITS identity, duplication, email degradation, PDF pagination, accessibility and operational isolation.

## Required challenges

1. **Authority:** every visible portfolio figure must derive from the normalized EU state; no donor holdings or U.S. investability assumptions may appear.
2. **Action semantics:** the page must distinguish model activity from a real brokerage transaction and must not imply a later tranche is approved.
3. **Cash semantics:** remaining cash must be described as capacity, not automatic deployment authority.
4. **Risk semantics:** EUNA may be described as a stabiliser, not guaranteed protection; VWCE/SXR8 overlap must remain visible as a discipline issue.
5. **History limits:** return and drawdown must not imply a richer observation history than the valuation series provides.
6. **Duplication:** successful full-page injection must suppress the compact investor summary strip while preserving section 1 as detailed rationale.
7. **Document order:** cockpit, investor report and analyst report must remain visually distinct and ordered.
8. **Email robustness:** essential hierarchy must survive removal of head-level CSS; hidden duplicate content must remain hidden through inline styling.
9. **PDF quality:** all seven pages per language require inspection for clipping, overflow, orphaned headings, broken glyphs and poor page transitions.
10. **Operational isolation:** preview execution may not modify portfolio state, pricing evidence, ledgers, recommendation memory or current production files.

## Initial findings

- A duplicate-summary risk was found in the first email-safe design because suppression depended on head CSS. The injector was changed to inline `display:none!important` before the first workflow run.
- The maximum-drawdown metric is based on a short valuation history. Final review must require a visible observation-count qualifier or record this as a blocker.
- The first page may still be too dense at A4 print scale; rendered evidence is required before acceptance.
- Section 1 remains intentionally present. Final review must decide whether it reads as useful detail or repetitive executive copy.

## Gate

```text
secondary_review_passed=false
rendered_evidence_reviewed=false
production_promotion_recommended=false
```

The gate may be changed only after machine validation and complete bilingual visual review.