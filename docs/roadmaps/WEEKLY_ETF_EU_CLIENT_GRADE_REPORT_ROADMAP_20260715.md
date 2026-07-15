# Weekly ETF EU Client-Grade Report Roadmap

Date opened: 2026-07-15  
Date completed: 2026-07-16  
Status: completed and promoted to routine production  
Workstream: `ETF-EU-RPT01_CLIENT_GRADE_REPORT_V2`

## Objective

Move the Weekly ETF EU product from a technically clean UCITS verification memo to a premium client-grade decision report, using `market-predictions/weekly-etf` as the architectural donor while preserving EU/UCITS authority.

Outcome:

```text
all_six_phases_completed=true
fresh_current_date_comparison_passed=true
promotion_smoke_passed=true
readiness_adapter_passed=true
production_renderer=client_grade_v2
```

## Completed architecture

```text
weekly-etf donor concepts
→ EU-specific normalized report state
→ current pricing and macro provenance
→ valuation-history update
→ conditional portfolio analytics
→ investor brief + analyst appendix
→ component-based Dutch and English renderer
→ strict client-grade validation
→ complete page-review evidence
→ routine production promotion
```

The EU repository remains the source of truth. U.S. holdings, ticker authority, recipient authority and funding assumptions were not copied.

## Phase 1 — Premium EU report contract — completed

One PDF per language now contains two coherent surfaces.

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

The validated current-date reports contain six pages per language.

## Phase 2 — Normalized EU runtime report state — completed

The renderer now consumes one run-scoped state artifact combining:

- EU portfolio state;
- EU valuation history;
- current UCITS pricing;
- UCITS registry;
- current macro-policy context;
- candidate and verification evidence.

```text
render_source_authority=normalized_report_state
markdown_role=decision_summary_audit_companion_not_v2_render_source
```

## Phase 3 — Valuation history and equity curve — completed

Implemented:

- deterministic valuation-history updates;
- current NAV reconciliation;
- deterministic SVG equity curve;
- cash-preservation fallback;
- automatic chart activation after meaningful validated history or a funded position.

The current cash-only model correctly shows the cash-preservation surface instead of a decorative flat graph.

## Phase 4 — Macro, opportunity and decision layers — completed

Implemented:

- current donor macro adaptation with provenance and freshness limits;
- regime and central-bank context;
- structural UCITS opportunity radar;
- risks and invalidations;
- allocation map;
- second-order effects;
- verification funnel;
- downside-risk and avoidance radar.

U.S. ETFs remain research references only. EU identity remains ISIN-first.

## Phase 5 — Component-based premium renderer — completed

Implemented:

- portrait A4 layout;
- premium masthead;
- investor/analyst separation;
- executive summary cards;
- numbered section badges;
- reusable panels and callouts;
- branded tables;
- conditional chart placement;
- print-aware pagination;
- Dutch-primary and English-companion parity;
- bilingual editorial polish.

The legacy three-page surface is no longer the routine production renderer.

## Phase 6 — Proportionate product-quality validation — completed

The promoted path validates:

- all fifteen report sections;
- investor/analyst hierarchy;
- Dutch and English client language;
- ISIN-first identity;
- research-only labelling;
- internal-metadata absence;
- chart/cash-callout correctness;
- page count;
- semantic tables;
- PDF completeness and visual quality.

Validation remains proportionate: one strict product contract plus complete page-review evidence, without a large parallel gate hierarchy.

## Promotion evidence

Fresh comparison:

```text
run_id=20260715_213100
workflow_run_id=29455916014
artifact_id=8359334286
promotion_recommended=true
blockers=[]
```

Promotion smoke:

```text
run_id=20260715_224700
workflow_run_id=29456627922
artifact_id=8359605163
strict_validation_passed=true
visual_review_passed=true
```

Readiness verification:

```text
run_id=20260715_225500
workflow_run_id=29457156167
artifact_id=8359792531
readiness_adapter_passed=true
```

Detailed evidence:

```text
control/evidence/ETF_EU_RPT01_CLIENT_GRADE_V2_PRODUCTION_PROMOTION_EVIDENCE_20260716.md
control/decisions/ETF_EU_RPT01_CLIENT_GRADE_V2_PRODUCTION_PROMOTION_DECISION_20260716.md
```

## Production boundary

The comparison and promotion verification performed no production action and did not modify portfolio state. The established run-specific authority and receipt layers remain separate from report generation.

## Final operating rule

Client-grade v2 is the routine production renderer. Normal weekly runs use the promoted path automatically. Repair concrete defects directly; restart architecture planning only for a genuine material capability change.
