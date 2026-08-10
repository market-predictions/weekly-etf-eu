# Weekly ETF EU Review OS — Current State

## Snapshot

```text
date=2026-08-10
repository=market-predictions/weekly-etf-eu
main_sha_at_reconciliation=3d97712a9bd135192f67b8c5dd860d295adbf5fc
operating_mode=DONOR_PARITY_RECONCILIATION_WITH_INDEPENDENT_RELEASE_ASSURANCE
current_work_package=ETF-EU-WP-DONOR-PARITY-RECONCILIATION-V1
active_claim=ETF-EU-DONOR-PARITY-RECONCILIATION-V1
working_branch=agent/etf-eu-donor-parity-reconciliation-v1
pull_request=91
issue=90
state=IMPLEMENTATION_CONVERGENCE_PRE_ASSURANCE
last_green_semantic_implementation_head=010b15152542efb931c5989584ffdea46f04363a
principal_decision_required=false
principal_action_required=false
portfolio_mutation=false
ledger_write=false
report_delivery=false
real_broker_execution=false
```

The final assurance head is not declared in this file because administrative closeout commits follow the semantic implementation head. The independent assurance issue must bind the exact live PR head after handover freeze.

## Current objective

Close the remaining Weekly ETF EU maturity gaps relative to the current Weekly ETF donor while preserving deliberate EU-specific UCITS/PRIIPs/KID/ISIN/exact-trading-line controls.

Parity means equivalent decision/state discipline where appropriate, not copying donor implementation weaknesses or U.S.-specific assumptions.

## Protected portfolio authority

Authority:

`output/etf_eu_portfolio_state.json`

| Ticker | ISIN | Venue | Shares |
|---|---|---|---:|
| VWCE | IE00BK5BQT80 | Xetra | 151 |
| EUNA | IE00BDBRDM35 | Xetra | 1,526 |
| SXR8 | IE00B5BMR087 | Xetra | 10 |
| L0CK | IE00BG0J4C88 | Xetra | 934 |

```text
cash_eur=50208.40
funded_position_count=4
model_portfolio_only=true
real_broker_execution=false
```

This repair line does not change shares, cash or the trade ledger.

## Allocation authority

Canonical contract:

`control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`

Authority order:

```text
explicit current allocation decision
> protected portfolio state + trade ledger
> current completed-close valuation + current recommendation evidence
> current donor opportunity state mapped to verified UCITS lines
> historical strategy/shadow context
```

Retired as current authority:

```text
50% maximum position
35% minimum cash
15% maximum new ETF
75% as a position cap
```

Research/shadow only unless separately adopted:

```text
25% turnover
18% AI-compute/semiconductor cap
```

Donor numeric disciplines retained only with their correct semantics:
- cash >3% plus a fully fundable actionable lane = deploy-or-explain review trigger, not a cash target;
- cash >5% = material cash disclosure/classification trigger, not a cash floor;
- roughly 40% effective single-factor exposure = concentration disclosure trigger, not a position/theme cap.

Historical `strategic_target_weight_pct`, `phase_target_weight_pct` and `target_weight_pct` values are preserved only as non-current CAP01/transition audit metadata in normalized runtime state. They may not appear as current client targets or create Hold/Add/Reduce authority.

## Donor-parity decision/state layer

Current implementation provides per-funded-holding machine memory for:
- fresh-cash test;
- would-initiate-today;
- would-initiate-at-current-weight;
- fresh-cash implication;
- thesis and implementation score;
- replaceability and action clock;
- replacement close/duel status;
- contribution/drag;
- factor overlap;
- hedge/ballast validity;
- cash-policy implication;
- override/next-review fields;
- required next action.

Missing current evidence remains `UNRESOLVED`; an old `last_action=Hold`, prior purchase or historical target may not silently become a current Hold decision.

`output/etf_eu_recommendation_scorecard.csv` is rebuilt per run and must contain exactly the funded ticker set, including L0CK.

## Discovery/fundability layer

Canonical contract:

`control/ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1.md`

Lineage:

```text
donor broad discovery
→ donor research proxy
→ UCITS mapping
→ ISIN/KID/exact trading line
→ pricing
→ current re-underwriting
→ explicit allocation decision
```

Mapping or pricing alone cannot fund a position. Unresolved identity, KID, exact-line, pricing or policy conditions fail closed.

## Client/output layer

A P0 shadow-renderer defect was found during the donor cross-audit: the funded renderer was rebuilding the old three-position/CAP01 surface after normalization, including a 7.50% reserve floor and strategic/phase target copy.

That overlay is now removed. Current behavior:
- allocation map comes from normalized current state;
- funded position count is dynamic and includes L0CK;
- historical target fields are not rendered as current targets;
- current-position table shows current weight plus re-underwriting status, not phase target;
- renderer fails closed on retired target/fixed-reserve/three-position phrases;
- every funded ticker must appear on the client surface.

NL and EN remain companion renders from one normalized state.

## Operational workflow authority

Canonical topology:

`control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`

### Candidate
`.github/workflows/run-weekly-etf-eu-routine.yml`
- non-main candidate branch only;
- build, pricing, normalization, bilingual rendering, machine validation and review evidence;
- may persist generated candidate evidence only to the candidate branch;
- cannot self-assure, merge, deliver or execute a broker action.

### Independent assurance
A separate `governance_release_assurance` reviewer must review one exact frozen candidate head and return:

`PASS | FAIL | INDETERMINATE`

Machine preflight is supporting evidence only and cannot issue independent assurance, merge authority or delivery authority.

### Delivery
`.github/workflows/send-weekly-etf-eu-controlled-transport.yml` is the only active real delivery route. It is main-only and requires:
- exact independently assured candidate head;
- approved report commit in main lineage;
- independent PASS reference;
- principal guarded-send authorization;
- SHA-256 binding for all six NL/EN MD/HTML/PDF artifacts.

Transport does not re-render the approved report. Inbox delivery is not successful until positive receipt evidence exists.

## Historical workflow cleanup

Nineteen historical activation/send/repair/preview workflows were renamed to `.yml.disabled`. They remain audit history but cannot execute through GitHub Actions.

Historical transition and CAP01 allocation YAML files are explicitly `HISTORICAL_NON_EXECUTABLE`.

## Validation status

On semantic implementation head `010b15152542efb931c5989584ffdea46f04363a`:
- donor-parity regression suite: PASS;
- funded-renderer authority regression: PASS;
- product-boundary validation: PASS;
- target-allocator shadow validation: PASS;
- transition-composition replay: PASS;
- shadow-CID transport validation: PASS;
- release evidence machine-preflight validation: PASS.

One legacy allocator-report-shadow job was still running at the last snapshot; exact final-head CI must be rechecked after administrative handover commits.

## Release boundary

PR #91 is not independently assured yet and remains draft during implementation closeout.

No merge, report delivery, portfolio mutation, ledger mutation or real broker execution is authorized by this state.
