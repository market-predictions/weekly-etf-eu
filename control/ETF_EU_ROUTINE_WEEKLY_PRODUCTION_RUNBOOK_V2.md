# ETF EU Routine Weekly Production Runbook V2

Date: 2026-08-10  
Status: canonical routine runbook  
Supersedes: `control/ETF_EU_ROUTINE_WEEKLY_PRODUCTION_RUNBOOK_V1.md` for current runs

## Purpose

Run one current Weekly ETF EU review from authoritative state through broad discovery, exact UCITS mapping, completed-close pricing, current capital re-underwriting, normalized report state, bilingual output, independent assurance and separately governed delivery.

This runbook keeps the mature Weekly ETF donor behavior where useful but applies EU-specific identity and investability authority.

## Authority prerequisites

Read and apply:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/WORK_CLAIMS.json
control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md
control/UCITS_ETF_REVIEW_CONTRACT_V1.md
control/UCITS_INVESTABILITY_RULES.md
control/CAPITAL_REUNDERWRITING_RULES.md
control/LANE_DISCOVERY_CONTRACT.md
```

Historical transition/Stage-1 policy is not current allocation authority.

## Phase 1 — Run identity and completed-close date

Create a unique:

```text
run_id
report_date
report_suffix
source_sha
```

The report date must be a valid current completed-close date under the pricing contract. No canonical routine workflow may hardcode a historical report date.

Previous reports and historical transition artifacts are context/evidence only.

## Phase 2 — Protected current state

Current quantity/cash authority:

```text
output/etf_eu_portfolio_state.json
output/etf_eu_trade_ledger.csv
```

Rules:

- preserve exact shares/cash unless a separate current allocation decision explicitly authorizes mutation;
- separate actual state from historical `strategic_target_weight_pct`, `phase_target_weight_pct` or scenario fields;
- prior report prose is never live holdings authority;
- model portfolio remains separate from real broker execution.

## Phase 3 — Broad discovery

Use the mature donor discovery behavior as research input:

```text
broad donor lane assessment
→ current donor opportunity state
→ EU research-proxy classification
→ UCITS mapping
```

Requirements:

- preserve the broad persistent bucket taxonomy;
- do not shrink research coverage to only historically funded or Stage-1 themes;
- candidate rows without an exact UCITS mapping remain research/watch rows, not fundable rows;
- U.S.-listed ETFs remain research proxies only.

## Phase 4 — Exact UCITS mapping and model investability

For a candidate to become model-investable/review-ready require, as applicable:

```text
ISIN
UCITS status
PRIIPs/KID status
exact share class
exact venue
exchange ticker
trading currency
usable current completed-close pricing line
liquidity/spread suitability evidence where available
```

### Broker-neutral rule

```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```

Do **not** block broker-neutral model investability merely because an account-specific broker symbol/permission has not been checked.

If real execution is separately authorized, broker/account permission, routing and execution mapping become mandatory at that later layer.

## Phase 5 — Current completed-close pricing

Build current pricing evidence for funded holdings first and then the relevant mapped challengers/candidates.

Funded valuation keeps the established strict multi-provider same-date and exact-line identity requirements.

Candidate pricing may have a weaker evidence tier for research comparison, but a candidate cannot become current funding authority unless the run-scoped fundability contract is satisfied.

No historical-cache or prior-report price may silently become current when fresh retrieval is feasible.

## Phase 6 — Current capital re-underwriting

Run current re-underwriting for every funded holding and relevant mapped candidate.

Required funded-holding memory:

```text
would_initiate_today
would_initiate_at_current_weight
thesis_status_or_score
implementation_status_or_score
contribution_or_drag
factor_or_overlap_flag
hedge_or_ballast_validity_if_applicable
cash_policy_implication
replaceable_status
review_age_or_action_clock
best_exact_ucits_alternative_if_available
required_next_action
override_reason_if_applicable
```

Rules:

- every holding must re-earn capital;
- a valid thesis does not automatically validate the current ETF/weight;
- weak/replaceable implementation requires a direct mapped-alternative duel where evidence permits;
- missing evidence produces `UNRESOLVED`/monitoring, not indefinite unqualified Hold;
- meaningful cash must be deployed or explicitly explained against current fundable opportunities;
- this behavior does not create a fixed cash minimum/maximum.

Output:

```text
output/etf_eu_recommendation_scorecard.csv
```

Current-run rows must cover every funded position.

## Phase 7 — Current allocation review

Candidate review scope is the **current mapped opportunity set**, not the frozen historical two-theme Stage-1 set.

Historical Stage-1 activation remains provenance only.

No current hard limits are inherited from `config/etf_eu_transition_policy_v1.yml`.

Specifically, current allocation cannot be constrained merely by historical:

```text
35% minimum cash
15% maximum new position
50% cash-first scenario
25% turnover scenario
18% semiconductor theme cap
historical maximum-position count
```

A new numerical hard cap requires an explicit current decision.

Current review may produce:

```text
hold
hold_with_override
add_from_cash_candidate
reduce_candidate
replace_partial_candidate
replace_full_candidate
close_candidate
monitor_unresolved
```

Only a separate validated allocation decision can create trade intents or mutate model state.

## Phase 8 — Overlap and concentration analytics

Use holdings-overlap evidence as analytical input.

Incomplete holdings coverage yields a **measured lower bound**.

Example semantic contract:

```text
embedded_semiconductor_exposure=measured_lower_bound
minimum_required_exposure=false
hard_cap=false
```

Do not show a lower bound as a required minimum/client control.

## Phase 9 — Macro provenance

Adapt donor macro context only when its underlying evidence date is current enough for the EU report date.

Bind:

```text
donor_source_identity_or_commit
donor_source_sha256
donor_report_or_as_of_date
eu_report_date
age_days
freshness_pass
```

Wrapper generation time does not refresh stale donor evidence.

Macro context remains descriptive; it cannot create funding or trade authority by itself.

## Phase 10 — One normalized current-run state

Build one normalized run-scoped state containing separately typed:

```text
actual_portfolio
current_valuation
current_reunderwriting
current_candidate_fundability
current_allocation_review
historical_transition_evidence
historical_target_metadata
macro_provenance
authority_flags
```

Required authority flags include:

```text
shadow_policy_used_for_current_allocation=false
retired_fixed_percentage_used=false
historical_stage1_candidate_gate_applied=false
historical_target_used_for_current_trade=false
broker_specific_permission_required_for_model=false
portfolio_mutation=false
real_broker_execution=false
```

## Phase 11 — Dutch-primary / English-companion report

Generate both languages from the same normalized state.

Client output must show:

- actual portfolio state;
- current recommendations/monitoring;
- current authoritative constraints only;
- current evidence limitations;
- measured overlap analytics with correct semantics.

Historical allocator variants and retired percentage controls are internal evidence and must not appear as current client policy.

## Phase 12 — Machine + visual validation

Required fail-closed checks include:

```text
all funded positions present and unique
shares/cash preserved
current recommendation scorecard covers all funded positions
no U.S.-listed ETF as funded EU holding
UCITS/KID/exact-line gates preserved
funded current pricing gate passed
shadow policy not used for current allocation
retired 35/15/50/25/18 controls absent from current client authority
Stage-1 allowlist absent as current candidate gate
embedded overlap labelled measured lower bound
broker-neutral model boundary correct
NL/EN decisions/numbers coherent
no internal authority leakage
PDF visual review passed
```

## Phase 13 — Donor-parity audit

Generate a machine-readable parity audit for the five layers:

```text
PARITY
EU_ADAPTED_PARITY
INTENTIONAL_EU_DIVERGENCE
GAP_BLOCKING
GAP_NONBLOCKING
```

No `GAP_BLOCKING` item may remain at release closeout.

Intentional EU divergences include at minimum:

- ISIN-first/exact-line identity;
- UCITS/PRIIPs/KID;
- U.S. ETFs research-only;
- Dutch-primary output;
- broker-neutral model investability;
- no real broker execution from report workflow.

## Phase 14 — Independent governance/release assurance

Implementation success is not release approval.

Bind assurance to the exact candidate head/package and independently reconstruct:

- source lineage;
- authority separation;
- state preservation;
- discovery/mapping/pricing/re-underwriting evidence;
- client-surface parity;
- machine/visual validation;
- product boundary.

Required verdict:

```text
PASS | FAIL | INDETERMINATE
```

Any repair after verdict requires a fresh candidate and fresh assurance.

## Phase 15 — Guarded delivery

Delivery is separate from report generation and assurance.

Only after explicit current delivery authority:

1. bind exact package hashes and recipients;
2. execute guarded transport;
3. record transport evidence;
4. independently verify receipt and expected attachments;
5. reconcile rather than resend if matching receipt already exists.

Never claim successful delivery from workflow success or SMTP invocation alone.

## Phase 16 — Closeout and handover

At terminal state:

- update `control/CURRENT_STATE.md`;
- update `control/NEXT_ACTIONS.md`;
- update roadmap/work-package acceptance state;
- log stable decisions and changelog;
- reconcile `control/WORK_CLAIMS.json`;
- create final handover with exact PR/head/evidence/assurance/disposition;
- reconcile central Control state;
- ensure originating claim is `CLOSED`, `TRANSFERRED` or `SUPERSEDED`, never silently ACTIVE.

## Completion definition

A routine report release is complete only when current evidence proves the five layers are coherent and independent assurance passes the exact candidate. A delivered run additionally requires real receipt/attachment evidence.
