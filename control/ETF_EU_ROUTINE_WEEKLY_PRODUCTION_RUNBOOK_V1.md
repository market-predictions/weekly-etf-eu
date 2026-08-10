# ETF EU Routine Weekly Production Runbook V2

Date: 2026-08-10
Repository: `market-predictions/weekly-etf-eu`
Status: CANONICAL

This runbook governs fresh Weekly ETF EU candidate generation. Delivery is a separate post-assurance operation.

## Authority
Read first:
1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/WORK_CLAIMS.json`
5. `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`
6. `control/ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1.md`
7. `control/UCITS_INVESTABILITY_RULES.md`

The closest mature `market-predictions/weekly-etf` implementation is the behavior donor. It is never authority for EU holdings, recipients, execution or delivery.

## Canonical separation
```text
candidate build + implementation validation
→ frozen candidate
→ independent governance_release_assurance
→ merge / exact-main validation
→ separately authorized guarded delivery
→ independent receipt/attachment confirmation
```

A candidate-build workflow must not send email, mutate the protected model portfolio or declare independent assurance on its own output.

## Phase 1 — Resolve current completed close
1. Create a fresh `run_id` and report suffix.
2. Resolve the latest plausible completed European trading date for the requested run.
3. Build pricing evidence and require the funded exact lines to prove the actual same close date.
4. If providers prove a different valid completed close (holiday/session effect), use evidence rather than a calendar guess.
5. Never hard-code a historical repair date into the canonical routine.

## Phase 2 — Current state and identity
Canonical live inputs:
```text
portfolio_state=output/etf_eu_portfolio_state.json
trade_ledger=output/etf_eu_trade_ledger.csv
valuation_history=output/etf_eu_valuation_history.csv
recommendation_scorecard=output/etf_eu_recommendation_scorecard.csv
ucits_registry=config/ucits_symbol_registry.yml
proxy_map=config/ucits_benchmark_proxy_map.yml
allocation_authority=control/ETF_EU_ALLOCATION_AUTHORITY_V1.md
```

Rules:
- protected portfolio state owns quantities and cash;
- registry owns instrument identity, never current portfolio funding state;
- previous reports are historical display/strategy context only;
- historical strategic target fields are not current allocation authority;
- exact share class + ISIN + venue + trading line + currency is canonical identity.

## Phase 3 — Donor discovery and EU fundability bridge
1. Read the latest donor lane artifact on or before the report date.
2. Preserve the donor breadth/challenger evidence.
3. Map donor research proxies through `config/ucits_benchmark_proxy_map.yml`.
4. For each mapped EU candidate require the applicable identity/KID/exact-line evidence.
5. Join current completed-close pricing.
6. Emit normalized fundability states under `ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1`.

Mapping or pricing is never funding authority.

## Phase 4 — Current funded pricing
For every protected funded position require:
- exact identity anchor;
- current completed close;
- current production pricing policy;
- same-date funded set;
- two-provider consensus where the production pricing contract requires it.

Missing funded current valuation evidence fails closed. Never use prior report prose as current price authority.

## Phase 5 — Current-position re-underwriting
Every funded holding receives current recommendation memory:
- would initiate today;
- would initiate at current weight;
- fresh-cash implication;
- thesis/implementation assessment where evidence exists;
- replaceability/action clock;
- alternative/duel status;
- contribution/drag;
- factor overlap;
- hedge/role validity where relevant;
- cash-policy implication;
- required next action.

Missing evidence is `Unresolved`, not a fabricated score.

Cash discipline ports donor behavior:
- cash >3% plus an actionable fully fundable lane requires deploy-or-explain review;
- cash >5% is a material position;
- neither threshold automatically creates a trade;
- there is no universal current ETF EU cash floor.

## Phase 6 — Allocation boundary
A routine report run is valuation/recommendation only unless a separate explicit allocation decision is supplied.

Current non-authority:
- retired 50% maximum position;
- retired 35% minimum cash;
- retired 15% maximum new ETF;
- 75% pricing-coverage threshold as position cap;
- transition-era 25% turnover and 18% semiconductor cap;
- fixed `Cash-first 50%` scenario;
- historical CAP01 static target weights.

A measured embedded exposure such as semiconductor overlap is descriptive lower-bound evidence, never a required allocation minimum.

Broker-neutrality:
```text
broker_specific_permission_required_for_model=false
broker_permission_required_for_real_execution=true
```
Model funding requires UCITS/KID/identity/exact-line/pricing/re-underwriting + explicit allocation decision. Account-level broker permission belongs only to a separately governed real-execution boundary.

## Phase 7 — Normalized report state
Build one run-scoped normalized state and apply `runtime/apply_etf_eu_donor_parity_contract.py` before rendering.

The state must include:
- protected current portfolio;
- current pricing lineage;
- current macro provenance;
- donor discovery bridge;
- recommendation memory for every funded holding;
- cash policy status;
- allocation authority metadata;
- explicit no-mutation/no-execution flags.

Refresh `output/etf_eu_recommendation_scorecard.csv` from this same normalized run state so recommendation memory cannot lag the funded portfolio.

## Phase 8 — Macro provenance
Use donor macro behavior only with provenance.
- preserve original donor evidence/report date;
- compute freshness from the source evidence date, not the EU wrapper creation timestamp;
- stale donor macro remains labelled historical context until refreshed;
- no wrapper may make stale evidence appear current.

## Phase 9 — NL/EN generation
Generate Dutch-primary and English-companion outputs from the same normalized state.

Rules:
- no independent Dutch research pass;
- no shadow allocation controls in current-control tables;
- no fixed cash-floor/target scenario in authoritative client copy;
- embedded overlap labelled as measured lower-bound exposure;
- exact four-position state (or whatever the protected state currently contains) must be consistent across all sections;
- no duplicate funded ticker rows;
- no broker-execution implication.

## Phase 10 — Machine and visual validation
Required checks include:
```text
state_valid=true
funded_position_set_matches_protected_state=true
recommendation_scorecard_matches_funded_set=true
donor_discovery_bridge_present=true
shadow_rules_executable=false
broker_neutrality_consistent=true
nl_en_numeric_state_parity=true
client_surface_shadow_leakage=false
pricing_gate_passed=true
visual_review_passed=true
```

Render all NL/EN PDF pages and inspect clipping, overlap, glyphs, hierarchy and state consistency.

## Phase 11 — Candidate persistence
Candidate generation may upload an Actions artifact and may persist evidence to its candidate branch. It must not write a pre-assurance candidate directly to protected `main` as a release shortcut.

Freeze:
- source SHA;
- generated artifact digest;
- report date/run identity;
- normalized state;
- pricing evidence;
- donor discovery bridge;
- recommendation scorecard;
- NL/EN HTML/PDF;
- machine/visual gates.

## Phase 12 — Independent assurance
A separate `governance_release_assurance` reviewer reconstructs the frozen candidate and returns exactly:
```text
PASS | FAIL | INDETERMINATE
```

Implementation may not certify itself. Reviewer may not mutate the candidate. Any repair requires a new exact candidate and fresh assurance.

## Phase 13 — Merge and exact-main validation
After PASS and unchanged head:
1. merge;
2. validate exact `main` where required;
3. reconcile work claim/branch/handover;
4. update CURRENT_STATE/NEXT_ACTIONS/decision/changelog records.

## Phase 14 — Guarded delivery (separate operation)
Only after explicit post-merge delivery authority:
1. bind the exact approved package;
2. execute controlled transport;
3. record transport result;
4. independently confirm matching inbox receipt and expected attachments;
5. reconcile an existing receipt rather than resend.

Generation, Actions success or SMTP no-exception is not delivery confirmation.

## Historical/diagnostic routes
Transition allocator, CAP01 first-tranche activation, Stage-1 dated activation and 2026-08-04/05 repair workflows are historical/diagnostic evidence only. They are not canonical routine funding or release authority after this V2 runbook takes effect.

## Completion definition
A candidate-generation cycle is complete at `ASSURANCE_READY`, not `DELIVERED`.
A delivered weekly run is complete only after independent PASS, merge/exact-main reconciliation, separately authorized transport and independent receipt/attachment evidence.
