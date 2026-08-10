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

## Historical target metadata
Historical activation records may contain fields such as:

```text
strategic_target_weight_pct
phase_target_weight_pct
target_weight_pct
```

Those fields are audit evidence for the historical CAP01/transition decisions that created or shaped earlier model positions. They are not current target-weight authority.

The current runtime normalization layer must:
- preserve those values under explicitly non-current historical metadata where audit continuity is useful;
- remove the live-looking target fields from normalized current position rows before client rendering;
- never use them to create a Hold/Add/Reduce decision;
- fail client rendering if `strategic target`, `strategisch doel`, `phase target` or `fasedoel` reappears as current portfolio guidance.

Current position sizing authority exists only when a new explicit allocation decision says so.

## Embedded exposure semantics
Measured thematic overlap is descriptive evidence, not a required minimum.

For example:
```text
embedded_semiconductor_lower_bound_pct_nav
```
means the minimum exposure observable from documented overlapping holdings coverage. It must be labelled `measured lower-bound exposure` (or Dutch equivalent), never `minimum semiconductor allocation`, `required minimum` or `control`.

## Donor review and disclosure triggers
Weekly ETF donor discipline contains numeric review triggers that are useful for ETF EU, but these must not be confused with allocation caps.

### Cash
- cash >3% **and** at least one fully fundable actionable lane exists → explicit deploy-or-explain review;
- cash >5% → cash is a material portfolio position and must be classified/discussed;
- the cash classification is one of `Tactical reserve`, `Uninvested residual`, `Risk reserve`, `Deployment candidate` when current evidence supports it;
- missing classification is `unresolved`, not permission to infer a reserve motive;
- neither threshold creates an automatic trade;
- neither threshold is a minimum or maximum cash target;
- there is no universal current ETF EU cash floor unless separately adopted.

### Factor concentration
The donor rule that a single effective factor above roughly 40% must be called concentration is imported as a **measurement/disclosure trigger only**.

```text
~40% effective factor exposure = CONCENTRATION_DISCLOSURE_TRIGGER
~40% effective factor exposure != POSITION_CAP
~40% effective factor exposure != THEME_CAP
~40% effective factor exposure != AUTOMATIC_REBALANCE_TRIGGER
```

The measurement should use the best available holdings/factor evidence and must state uncertainty where look-through coverage is incomplete.

### Loss / inertia / replaceability
Donor action-clock triggers are re-underwriting triggers, not automatic trade orders. Examples include:
- `Hold but replaceable` persisting for two consecutive runs → direct alternative decision required;
- drawdown >10% with weak implementation evidence → re-underwrite from scratch;
- >7 percentage-point portfolio underperformance for two consecutive runs → re-underwrite.

Any actual size change still requires a separately governed current allocation decision.

## Fresh-cash / re-underwriting behavior
Every funded holding must be re-underwritten each routine run. Normalized decision memory should expose:
- would initiate today: `Yes | Smaller | No | Unresolved`;
- would initiate at current weight: `Yes | No | Unresolved`;
- fresh-cash implication: `Add | Hold | Reduce | Replace | Close | Watch one more week | Review required`;
- thesis score;
- implementation score;
- replaceability/action clock;
- best alternative and replacement-close/duel status;
- contribution/drag;
- factor overlap;
- hedge/ballast validity where relevant;
- cash-policy implication;
- override reason where used;
- next-review trigger and maximum review window where applicable;
- required next action.

A current `Hold` may not be inferred from an old purchase, old `last_action`, old target weight or the mere absence of a new trade. If current evidence is incomplete, re-underwriting is explicitly `UNRESOLVED` and the report must say what evidence/decision is still required.

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
