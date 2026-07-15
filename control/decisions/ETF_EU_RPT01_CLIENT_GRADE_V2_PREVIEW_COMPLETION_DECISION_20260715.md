# ETF EU RPT01 Client-Grade v2 Preview Completion Decision

Date: 2026-07-15
Status: adopted

## Decision

The six client-grade development phases are complete as one integrated preview implementation.

```text
workstream=ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2
preview_run_id=20260715_190000
workflow_run_id=29442173869
strict_validation_passed=true
validation_blockers=0
full_visual_review_passed=true
production_promotion=false
```

## Donor architecture used

The implementation adapted these mature `market-predictions/weekly-etf` concepts:

- normalized runtime report state;
- investor brief plus analyst appendix;
- executive summary cards and decision cockpit;
- macro and policy client surface;
- structural opportunity radar;
- allocation map and second-order effects;
- deterministic equity-curve contract;
- component-based print renderer;
- bilingual editorial polish;
- strict client-output validation.

The implementation did not copy U.S. holdings, U.S. instrument authority, U.S. funding authority, recipient authority or delivery assumptions.

## EU-specific implementation

The v2 surface remains:

```text
ISIN-first
UCITS-first
Dutch-primary
U.S. ETFs research-only
cash-only until a separate allocation decision
```

The current model portfolio has one validated cash-only NAV observation. Therefore, the report correctly shows a cash-preservation callout rather than a decorative flat equity graph. The SVG graph and valuation-history updater are implemented and activate when meaningful validated history exists.

## Product result

The final preview contains six pages in each language and includes:

### Investor brief

1. Decision cockpit
2. Portfolio and capital
3. Regime and policy dashboard
4. Structural UCITS opportunity radar
5. Key risks and invalidations
6. Portfolio development
7. Conclusion

### Analyst appendix

8. Allocation map
9. Second-order effects
10. UCITS candidates and pricing evidence
11. Verification funnel
12. Current-position review
13. Replacement, rotation and avoidance radar
14. Input for the next run
15. Disclaimer

Conditional position, replacement and equity-curve surfaces remain inactive while the portfolio is fully in cash, but their activation contracts are implemented.

## Validation and visual review

The standalone strict validator proved:

- all sections present in Dutch and English;
- investor and analyst hierarchy present;
- six pages in both languages;
- ISIN-first evidence visible;
- U.S. references labelled research-only;
- no raw workflow, authority or status enums;
- truthful cash-callout/equity-curve behavior;
- stale macro evidence visibly disclosed;
- no transport or portfolio mutation.

All six Dutch and all six English pages were visually inspected. No clipping, overlap, broken Unicode or raw Markdown leakage remained.

## Remaining boundary

The v2 implementation is not yet the production renderer.

Before promotion, run one fresh current-date v2 shadow report using the same current state, pricing and refreshed macro artifacts as the next routine production cycle. If that comparison passes, one explicit promotion decision may replace the production renderer.

No additional architecture packages or phase-by-phase approval loops are required.

## Next development action

```text
RUN_FRESH_CURRENT_DATE_V2_SHADOW_AND_DECIDE_PROMOTION
```
