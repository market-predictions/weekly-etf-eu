# ETF EU Allocation Authority V1

Date: 2026-08-10
Status: CANONICAL

## Purpose
This contract defines which allocation facts may drive the Weekly ETF EU model portfolio and which historical/shadow values are diagnostic only.

## Authority order
```text
1. explicit current allocation decision
2. protected portfolio state + trade ledger
3. current completed-close valuation and current recommendation evidence
4. current donor opportunity state mapped to verified UCITS trading lines
5. historical strategy context and shadow scenarios
```

Lower-ranked evidence may not silently override higher-ranked authority.

## Retired unsupported shadow rules
The following values are not current portfolio constraints and may not drive funding, sizing or client-facing current-control copy:

```text
50% maximum position = RETIRED_UNSUPPORTED_SHADOW_RULE
35% minimum cash = RETIRED_UNSUPPORTED_SHADOW_RULE
15% maximum new ETF = RETIRED_UNSUPPORTED_SHADOW_RULE
75% = PRICING_COVERAGE_CONTEXT_NOT_POSITION_CAP
```

## Research-only transition values
The transition-era 25% gross-turnover ceiling and 18% AI-compute/semiconductor theme cap were created inside a `shadow_only` transition-policy artifact. They have not been separately adopted as current ETF EU allocation authority.

Therefore:
```text
25% turnover = RESEARCH_SHADOW_ONLY
18% semiconductor cap = RESEARCH_SHADOW_ONLY
```

They may remain in historical diagnostic artifacts, but may not:
- size a current model trade;
- block current model funding;
- appear as a current client control;
- be treated as a durable donor rule.

Any future adoption requires an explicit decision artifact with rationale, scope, tests and effective date.

## Embedded exposure semantics
Measured thematic overlap is descriptive evidence, not a required minimum.

For example:
```text
embedded_semiconductor_lower_bound_pct_nav
```
means the minimum exposure observable from documented overlapping holdings coverage. It must be labelled `measured lower-bound exposure` (or Dutch equivalent), never `minimum semiconductor allocation`, `required minimum` or `control`.

## Cash authority
Cash is an active portfolio position. The donor discipline is imported as behavior:
- cash >3% with an actionable, fully fundable lane requires an explanation or an allocation decision;
- cash >5% is material and must be discussed;
- neither rule is an automatic trade instruction;
- there is no universal ETF EU cash floor unless separately adopted.

## Fresh-cash / re-underwriting behavior
Every funded holding must be re-underwritten each routine run. Normalized decision memory should expose where evidence permits:
- would initiate today;
- would initiate at current weight;
- thesis versus implementation assessment;
- replaceability/action clock;
- best alternative and duel status;
- factor overlap;
- contribution/drag;
- cash-policy implication;
- required next action.

Missing evidence is `unresolved`, not permission for indefinite Hold.

## Broker-neutrality
Model investability requires UCITS/KID/identity/exact-line/pricing/fundability evidence. It does not require account-level broker permission.

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

## Position-count rule
The donor currently has an explicit maximum-active-position contract. ETF EU must not inherit that number from a historical transition file by accident. Until a separate ETF EU decision explicitly adopts a maximum, position count is a portfolio-review dimension rather than a hard funding cap.

## Execution boundary
A report, shadow allocator, research scenario, donor target, client narrative or recommendation cannot create a trade. Only a separately governed explicit allocation decision may authorize model portfolio mutation, and real broker execution remains separately authorized again.
