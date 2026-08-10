# ETF EU Capital Re-underwriting Rules

## Purpose

This is the EU/UCITS adaptation of the mature Weekly ETF donor capital-discipline layer.

It answers one recurring question every run:

> If this position did not exist today, would the EU model initiate this exact UCITS line now, at this weight, with fresh capital?

The contract is behavioral decision discipline. It does **not** create new hard allocation caps and does not authorize portfolio mutation.

Authority:

`control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md`

## Placement

Run after current portfolio valuation and broad discovery/UCITS mapping, and before any new allocation decision or final action table.

For every funded holding assess:

1. fresh-cash test;
2. thesis versus implementation;
3. direct exact-UCITS alternative duel when relevant;
4. contribution / drag;
5. factor and holdings-overlap risk;
6. hedge/ballast validity where relevant;
7. cash policy;
8. action clock / inertia;
9. current pricing and fundability of any proposed alternative.

## Fresh-cash test

Required current-run fields:

| Test | Allowed values |
|---|---|
| Would initiate today? | Yes / Smaller / No / Unresolved |
| Would initiate at current weight? | Yes / No / Unresolved |
| Fresh-cash implication | Add candidate / Hold / Reduce candidate / Replace candidate / Close candidate / Monitor unresolved |

Rules:

- `Unresolved` is allowed when current evidence is incomplete, but it cannot create a new trade.
- If the position would not be initiated today at any size, unqualified Hold is not sufficient.
- If it would only be initiated smaller, mark Reduce/under-review or record an explicit override.
- An override must name the reason and next-review trigger.

## Thesis versus implementation

Separate:

- **Thesis** — is the macro/structural/portfolio role still valid?
- **Implementation** — is this exact UCITS ETF/share class/venue/weight still the best implementation?

A strong thesis does not automatically justify the current ETF or current weight.

If thesis is strong but implementation is weak, force a direct alternative duel where a verified UCITS candidate exists.

## Exact-UCITS alternative duel

A direct replacement duel is required when a holding is replaceable, weakening or has a clearly superior mapped challenger.

Minimum evidence where available:

| Test | Current holding | EU alternative |
|---|---|---|
| ISIN + exact trading line | | |
| UCITS/KID | | |
| Latest completed close/date | | |
| 1m/3m relative strength | | |
| Liquidity/spread | | |
| Theme/role purity | | |
| Drawdown | | |
| Portfolio differentiation/overlap | | |
| Implementation cost/TER | | |
| Final verdict | | |

A U.S.-listed donor ETF may be the research comparator but never the replacement instrument in the model portfolio.

If the EU alternative is not fully mapped/priced, the duel is `UNRESOLVED`; it is not permission for an automatic replacement.

## Replacement fundability status

Allowed states:

```text
fundable_replacement_candidate
mapped_priced_reunderwriting_required
priced_but_duel_incomplete
mapped_but_current_pricing_missing
mapping_required_research_only
not_fundable_identity_or_kid_blocked
```

A same-run model switch requires compatible current completed-close evidence for both sides and a separate allocation decision.

## Contribution / drag

Each current position should state whether it is:

```text
strong_positive_contributor
positive_contributor
flat_or_opportunity_cost
material_drag
unresolved
```

Historical P&L alone is not a reason to keep or close a position; contribution must be considered with current thesis, implementation and opportunity cost.

## Factor and holdings-overlap test

Assess economic exposure, not just ticker count.

Relevant EU examples include:

- U.S. mega-cap / AI sentiment embedded in VWCE/SXR8;
- semiconductor exposure embedded in broad core funds plus a semiconductor satellite;
- cybersecurity exposure embedded in broad funds plus L0CK;
- equity beta versus EUNA ballast;
- regional diversification and currency exposure.

Incomplete holdings data produces a **measured lower bound**, never an assumed complete exposure.

The donor's approximately 40% factor-concentration threshold may be used as a **review/warning trigger**, not as a hard ETF EU allocation cap.

No numerical theme cap is created by this rule.

## Hedge / ballast validity

For any ballast/hedge role, including bond stabilisers where relevant, review:

- realized protection/contribution during equity stress;
- current verified pricing;
- drawdown and duration/rate sensitivity;
- whether the position still diversifies the current portfolio;
- whether a better exact UCITS alternative exists.

A ballast role is not a permanent exemption from re-underwriting.

## Cash policy

Cash is a meaningful active portfolio position.

Behavioral review triggers ported from the donor:

- cash above ~3% plus a genuinely actionable/fundable lane requires deploy-or-explain review;
- cash above ~5% should be described as a meaningful portfolio position.

These are **review triggers**, not minimum or maximum cash constraints.

Do not reintroduce the retired 35% minimum cash or a fixed 50% cash-first target.

If opportunities are unmapped, unpriced, KID/identity-blocked or re-underwriting-incomplete, retained cash is a legitimate governed result.

## Action clock / inertia

A weak or replaceable position cannot remain indefinitely in ambiguous Hold.

Behavioral rules:

- a position tagged replaceable/under review for two consecutive runs should receive a direct decision or explicit evidence-based override;
- a materially loss-making position with weak implementation should be re-underwritten from scratch;
- persistent material underperformance versus portfolio/alternative should trigger re-underwriting;
- any override carries a next-review trigger and review-age memory.

These rules guide decision quality; they do not auto-execute trades.

## Current recommendation scorecard

Canonical current-run memory:

`output/etf_eu_recommendation_scorecard.csv`

Every funded position must appear once per current run.

Minimum fields include:

- report date;
- ISIN and exact exchange ticker;
- current weight/shares/price evidence status;
- fresh-cash test;
- would initiate today / at current weight;
- thesis and implementation status/score when supported;
- replaceable status and review age;
- best exact-UCITS alternative when available;
- contribution quality;
- factor/overlap flag;
- hedge/ballast status;
- cash-policy flag;
- required next action;
- override reason;
- evidence/fundability status.

Missing current evidence must be represented as `Unresolved`/`CURRENT_REVIEW_REQUIRED`, not silently copied from a stale report.

## Allocation authority boundary

This contract can recommend review outcomes but cannot by itself create trade intents.

Current allocation authority remains:

```text
explicit current allocation decision
> protected portfolio state and trade ledger
> current completed-close valuation and exact-line identity
> current re-underwriting/overlap/fundability evidence
> current donor opportunity state after EU mapping
> historical strategy/shadow context
```

Historical Stage-1 limits and shadow percentages do not constrain current re-underwriting.

## Report integration

The report should surface only decision-relevant outcomes:

- main discipline issue;
- cash deploy-or-explain result;
- positions under review;
- best mapped alternative where material;
- unresolved evidence and next trigger;
- overlap/concentration warning with correct lower-bound semantics.

Internal score mechanics and historical allocator scenarios stay out of the client control table.

## Definition of done

Re-underwriting is operational when every funded holding has a current-run scorecard row, unresolved evidence blocks new action rather than creating inertia, relevant alternatives are exact-UCITS mapped before being called fundable, cash is actively explained, and action-clock memory survives into the next run.
