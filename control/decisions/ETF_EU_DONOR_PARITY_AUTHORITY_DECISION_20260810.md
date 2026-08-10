# ETF EU Donor-Parity Authority Decision — 2026-08-10

Status: `STABLE_PROJECT_DECISION`
Issue: #90
PR: #91

## Decision

Weekly ETF EU adopts the mature Weekly ETF donor's **decision and state disciplines** where they are product-neutral, but does not copy U.S.-specific instrument assumptions or donor operational weaknesses.

## Stable rules

### Allocation/state
1. Current allocation authority is:

   `explicit current allocation decision > protected portfolio + ledger > current completed-close valuation + current recommendation evidence > mapped donor opportunity state > historical/shadow context`.

2. Historical 50% maximum-position, 35% minimum-cash and 15% maximum-new-ETF values are retired unsupported shadow rules.
3. 75% means pricing-coverage context, not a position cap.
4. Historical 25% turnover and 18% semiconductor/theme values remain research/shadow only until separately adopted.
5. Historical `strategic_target_weight_pct`, `phase_target_weight_pct` and `target_weight_pct` are audit metadata only and may not appear as current target authority.
6. A report, renderer, shadow allocator, historical action or absence of a trade cannot create current Hold/Add/Reduce authority.

### Donor parity
7. Every funded position must be re-underwritten each routine run using current evidence.
8. Missing current evidence is `UNRESOLVED`, not implicit Hold.
9. Cash >3% with a fully fundable actionable lane is a deploy-or-explain review trigger; cash >5% is a material-position classification/disclosure trigger. Neither is a cash target.
10. Roughly 40% effective single-factor exposure is a concentration disclosure/review trigger, not a position or theme cap.
11. Replaceability/action-clock, contribution/drag, factor overlap, hedge validity and direct challenger duels are current review disciplines, not automatic trade instructions.

### EU-specific product gates
12. EU investability remains ISIN-first, UCITS/PRIIPs/KID-aware and exact-trading-line specific.
13. U.S.-listed ETFs are research proxies only unless a separate EU instrument contract says otherwise.
14. Discovery lineage is:

   `donor broad discovery → research proxy → UCITS mapping → ISIN/KID/exact line → pricing → re-underwriting → explicit allocation decision`.

15. Mapping or pricing alone cannot create funding authority.
16. Model investability is broker-neutral; broker permission belongs only to real execution where applicable.

### Release/delivery governance
17. Candidate generation, independent assurance, merge/exact-main validation and delivery are separate operational stages.
18. Implementation/CI machine evidence is preflight evidence only; it cannot issue an independent assurance verdict.
19. Independent `governance_release_assurance` must review one exact frozen head and return `PASS | FAIL | INDETERMINATE`.
20. Any semantic head change after review invalidates the verdict.
21. Real ETF EU email transport uses one controlled main-only route bound to independent PASS, an approved main-lineage report commit, principal guarded-send authorization and SHA-256 hashes of the exact approved client artifacts.
22. Transport must not re-render an assured package.
23. Delivery is not successful without positive independent receipt/attachment evidence.
24. Report workflows never authorize real broker execution.

## Intentional non-parity

Weekly ETF EU may be stricter than the donor where that removes a known operational weakness. In particular, ETF EU does not preserve historical report-to-state authority inversion or parallel legacy send routes merely for symmetry.

## Consequence

Future sessions must not rediscover or reintroduce retired CAP01/transition controls from old reports, target-allocation YAML, shadow allocators, renderers or historical workflow files. Any proposed new hard allocation cap requires a new explicit decision with rationale, scope, effective date and tests.
