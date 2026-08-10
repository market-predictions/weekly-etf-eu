# Weekly ETF EU — Donor Parity Reconciliation Roadmap

Date: 2026-08-10
Issue: #90
PR: #91
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`
Status: `REPAIR_IMPLEMENTATION_COMPLETE_PRE_HANDOVER`

## Goal
Bring `weekly-etf-eu` to behavioral parity with the mature `weekly-etf` donor wherever product behavior should match, while preserving deliberate EU-specific UCITS/ISIN/KID/exact-trading-line requirements.

Governing rule: **port behavior, not U.S. assumptions**.

## Assurance history

Independent issue #92 reviewed frozen head:

`a9f93af018623011ac4b2cae742d69ea1441b4ca`

and returned:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: FAIL`

That failed candidate remains historical evidence only and has no merge or delivery authority.

The reviewer accepted the decision/allocation authority work and identified two executable blockers:
1. incoherent pricing v2 builder → validator → normalized-state contract plus missing exact report-date/funded-consensus binding;
2. hard-coded three-position Markdown delivery copy omitting L0CK.

Repair package:

`control/work_packages/ETF_EU_PR91_ASSURANCE_FAIL_REPAIR_V1_20260810.md`

## Five-layer status

### 1. Decision framework — COMPLETE / NOT REOPENED
- retired 50% maximum position, 35% minimum cash and 15% maximum new ETF remain non-executable;
- 75% remains pricing coverage, not a position cap;
- 25% turnover and 18% semiconductor/theme values remain research/shadow only;
- embedded thematic exposure remains descriptive lower-bound evidence;
- donor cash >3%/>5% and ~40% factor thresholds remain review/disclosure triggers, not allocation caps;
- fresh-cash, replacement-duel, action-clock, contribution, hedge and factor-overlap concepts remain represented.

### 2. Input/state contract — COMPLETE AFTER FAIL REPAIR
Canonical pricing path is now:

```text
candidate request report_date
→ provider qualification on exact report_date
→ ucits_close_price_validation_basket_results_v2
→ funded two-provider same-date consensus
→ shared v2 validator
→ v2 normalized state
→ candidate package
```

Negative cases fail closed: v1 schema, report-date drift, missing funded line, one-provider funded evidence and failed funded consensus.

The hidden legacy package-level `min_threshold_met`/priced-line-count release gate is removed. Historical compatibility data is not current pricing authority.

Funded reconciliation metadata is persisted in normalized state so renderer and validator use the same four-position authority.

### 3. Output contract — COMPLETE AFTER FAIL REPAIR
NL/EN Markdown is now a first-class state-derived delivery artifact:
- dynamic funded count;
- exact current funded ticker set including L0CK;
- no hard-coded VWCE/EUNA/SXR8-only current-position surface;
- three-position wording fails closed;
- retired strategic/phase targets and fixed 7.50% reserve wording fail closed;
- discovered mixed-language NL leakage fails closed;
- Markdown is validated alongside HTML/PDF;
- internal machine enum `funded_model_position_active` is normalized to client-safe language before final HTML/PDF persistence.

### 4. Operational runbook — COMPLETE
- candidate → independent assurance → merge/exact-main → separately authorized guarded delivery;
- candidate route remains non-main and cannot self-assure/merge/deliver;
- 20 historical/parallel routes remain disabled;
- three donor-shadow workflows remain research-only;
- controlled transport remains the sole real delivery route;
- candidate pricing is explicitly bound to `ETF_EU_REPORT_DATE` and funded consensus;
- Markdown QA is persisted with candidate evidence.

### 5. Governance/release assurance — READY FOR NEW HANDOVER CYCLE
- issue #92 = immutable historical FAIL record;
- repair implementation is complete;
- semantic implementation baseline `19954692ff8b33d5ffac9b09d6654210a7194997` is fully green;
- a new final handover commit will produce the fresh frozen assurance SHA;
- a new independent assurance issue distinct from #92 is mandatory.

## Execution waves

### Wave A — Authority repair — COMPLETE
### Wave B — Donor-parity state and decision layer — COMPLETE
### Wave C — Canonical routine convergence — COMPLETE
### Wave D1 — Assurance-fail repair — COMPLETE

Evidence on semantic baseline `19954692ff8b33d5ffac9b09d6654210a7194997`:
- donor parity/full six-artifact package regression run `31433054217` — SUCCESS, `31 passed`;
- product boundary `31433053898` — SUCCESS;
- release evidence preflight `31433054597` — SUCCESS;
- shadow CID transport validation `31433054225` — SUCCESS;
- strategy synchronization shadow `31433054231` — SUCCESS;
- target allocator shadow `31433054316` — SUCCESS;
- transition composition replay `31433054295` — SUCCESS.

Additional donor-parity job evidence:

```text
ETF_EU_WORKFLOW_AUTHORITY=PASS
ETF_EU_CANDIDATE_PRICING_AND_MARKDOWN_WIRING=PASS
ETF_EU_DONOR_PARITY_STATIC_AUTHORITY_AUDIT=PASS
```

### Wave D2 — Fresh assurance and lifecycle closeout — NEXT
Definition of done:
1. governance/current-state/claim files reconciled around the completed repair;
2. repair handover written as final candidate mutation;
3. resulting live PR #91 head frozen;
4. fresh independent assurance issue returns `PASS`;
5. reviewed head remains unchanged;
6. PR #91 merged;
7. exact-main validation green;
8. issue #90 and integration claim closed;
9. project and central Control state reconciled;
10. no report delivery claimed from this repair line.

## Donor-parity matrix

| Donor behavior | ETF EU implementation | Status |
|---|---|---|
| State outranks Markdown | protected/current normalized state governs MD/HTML/PDF | PARITY |
| Fresh-cash re-underwriting | current per-funded-position memory; missing evidence unresolved | PARITY |
| Thesis vs implementation | explicit separate fields | PARITY |
| Direct alternative duel | replacement close/duel memory | PARITY |
| Action clock | replaceability timer/escalation | PARITY |
| Contribution/drag | current contribution fields | PARITY |
| Factor overlap | ~40% disclosure trigger, not cap | PARITY |
| Hedge validity | explicit ballast/hedge validity review | PARITY |
| Cash policy | >3% deploy-or-explain conditional; >5% material disclosure | PARITY |
| Broad discovery before runtime | donor-lane → UCITS bridge before fundability | PARITY WITH EU GATES |
| Pricing evidence boundary | exact report-date funded two-provider consensus under one v2 contract | PARITY |
| Challenger pricing is not funding | fundability + explicit allocation boundary | PARITY |
| Bilingual single-state output | NL/EN MD/HTML/PDF from one normalized state | PARITY |
| U.S. security identity | ISIN-first UCITS/KID/exact-line identity | INTENTIONAL EU DIVERGENCE |
| Legacy operational routes | stricter candidate/assurance/delivery separation | INTENTIONAL EU HARDENING |

## Intentional EU divergences to preserve
- ISIN-first identity and exact share class/trading line;
- UCITS + PRIIPs/KID model-investability gates;
- U.S.-listed ETFs as research proxies only;
- EUR trading-line preference where practical;
- Dutch-primary client output;
- broker-neutral model portfolio;
- no real broker execution from report workflow;
- stricter independent release/delivery role separation.

## Stop/escalation criteria
Escalate to the principal only for a genuine strategic choice that cannot be derived from donor behavior or existing EU authority. No principal decision is required for the current fresh-assurance handover.
