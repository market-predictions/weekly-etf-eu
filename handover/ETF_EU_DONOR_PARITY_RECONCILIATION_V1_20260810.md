# ETF EU Donor-Parity Reconciliation V1 — Implementation Handover

Date: 2026-08-10
Disposition: `HANDOVER_READY`
Implementation role: `implementation_operations`
Independent review role required: `governance_release_assurance`
Issue: #90
PR: #91
Branch: `agent/etf-eu-donor-parity-reconciliation-v1`
Target: `main`
Base/main SHA at handover preparation: `3d97712a9bd135192f67b8c5dd860d295adbf5fc`
Last fully validated pre-handover head: `26836da0222b5569ac7d89f6e44fdca497c89a6a`

## Freeze rule

This handover and the `HANDOVER_READY` claim transition are committed atomically as the final implementation mutation on PR #91.

The exact independent-assurance candidate is therefore **the live PR #91 head resulting from the commit that contains this handover**, not the pre-handover SHA printed above. The assurance issue must read that SHA live, record it explicitly, and review only that exact head.

No further candidate mutation is permitted after freeze. Any semantic or administrative change to the candidate after the independent review starts invalidates the verdict and requires a fresh frozen head plus fresh assurance.

## Objective completed

Close Weekly ETF EU gaps and recurring inconsistencies relative to the mature Weekly ETF donor without copying U.S.-specific assumptions or weakening EU UCITS/KID/ISIN/exact-line controls.

The work was deliberately split across decision framework, input/state contract, output contract, operational runbook and governance/release assurance.

## Implementation summary

### Decision framework
- Installed canonical `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`.
- Retired unsupported 50% maximum-position, 35% minimum-cash and 15% maximum-new-ETF shadow rules.
- Fixed 75% semantics as pricing-coverage context, not a position cap.
- Kept historical 25% turnover and 18% semiconductor/theme values research-only unless separately adopted.
- Imported donor >3%/>5% cash and ~40% factor thresholds strictly as review/disclosure triggers, not allocation caps.
- Preserved measured thematic overlap as descriptive lower-bound exposure, never a required minimum.

### Input/state contract
- Protected portfolio remains four funded positions: VWCE, EUNA, SXR8, L0CK; shares/cash unchanged.
- Recommendation memory is rebuilt for every funded position.
- Current re-underwriting exposes fresh-cash, thesis/implementation, replacement duel, contribution, factor overlap, hedge validity, cash-policy, action-clock and next-action fields.
- Missing current evidence is explicitly `UNRESOLVED`; no implicit Hold from old actions, purchases or target weights.
- Historical `strategic_target_weight_pct`, `phase_target_weight_pct` and `target_weight_pct` are isolated as non-current audit metadata before rendering.
- UCITS registry is identity/investability-only; funded state remains in protected portfolio authority.
- Model investability is broker-neutral; broker permission belongs only to real execution.
- Macro freshness is bound to donor provenance source date.
- Completed-close resolution is dynamic rather than tied to the 2026-08-05 repair date.

### Output contract
- Removed the post-normalization funded shadow renderer behavior that recreated a 7.50% reserve floor, strategic/phase targets and hard-coded three-position copy.
- Funded count/tickers are dynamic and include L0CK.
- Current-position output shows current weight plus re-underwriting status, not historical target columns.
- Client rendering fails closed on retired reserve/target/three-position phrases and on missing funded tickers.
- NL-primary and EN-companion output derive from one normalized state.
- Retired the old allocator `sister report` workflow so historical transition/shadow allocation state cannot render a second client-like report surface.

### Operational runbook
- Canonical candidate workflow is non-main only and cannot self-assure, merge, push candidate output to main, deliver or execute a broker action.
- Machine release evidence is preflight/supporting evidence only; it cannot issue independent assurance, merge authority or delivery authority.
- Twenty historical activation/send/repair/preview/client-like shadow routes are retained only as `.yml.disabled` audit history.
- The immutable donor pin registers exactly three active research-only donor synchronization workflows and separately records the allocator sister-report route as retired.
- Controlled transport is the sole active real ETF EU delivery route.
- Guarded transport requires exact independent PASS, approved report commit in main lineage, separate principal guarded-send authorization and SHA-256 binding of all six NL/EN MD/HTML/PDF client artifacts.
- Controlled transport sends exact approved artifacts and does not re-render them.
- SMTP transport success remains insufficient for a delivery-success claim; positive independent receipt/attachment evidence is required.

### Governance
- One surviving release-integration claim: `ETF-EU-DONOR-PARITY-RECONCILIATION-V1`.
- Old PR80 line is superseded; V3/PR84 line is closed.
- Stable decisions are recorded in `control/decisions/ETF_EU_DONOR_PARITY_AUTHORITY_DECISION_20260810.md`.
- Roadmap, work package, SYSTEM_INDEX, CURRENT_STATE, NEXT_ACTIONS, workflow authority index and governance changelog point to the PR #91 architecture.

## Protected boundaries verified

Throughout this work package:

```text
portfolio_mutation=false
trade_ledger_write=false
real_broker_execution=false
report_delivery=false
smtp_send=false
funding_authority_from_report_text=false
independent_assurance_from_implementation=false
```

No shares, protected cash or trade-ledger records were changed by PR #91.

## Pre-handover exact-head evidence

All required implementation and intentionally retained research-only gates completed successfully on:

`26836da0222b5569ac7d89f6e44fdca497c89a6a`

Successful runs:
- donor parity + funded-renderer/workflow-authority regressions — run `31406660053` — PASS;
- Weekly ETF EU product boundary — run `31406660059` — PASS;
- release-evidence machine preflight contract — run `31406660224` — PASS;
- shadow CID transport validation — run `31406660120` — PASS;
- strategy synchronization shadow — run `31406660046` — PASS;
- transition composition replay — run `31406660055` — PASS;
- target allocator shadow — run `31406660045` — PASS.

The obsolete allocator-report-shadow workflow is not a release gate; it was retired because it created a parallel client-like sister report from historical transition policy. Its removal initially exposed a stale donor-pin registration; the pin and validator were repaired and the three remaining research-only donor validations then passed on the SHA above.

## Changed-scope evidence

PR #91 includes, by category:
- canonical authority/control contracts;
- donor-parity runtime normalization and discovery/fundability bridge;
- funded renderer repair;
- request/delivery/workflow validators;
- candidate-only and guarded-delivery workflows;
- historical workflow `.disabled` moves;
- historical allocation config authority markers;
- UCITS registry/proxy mapping cleanup;
- macro/close-date adaptations;
- deterministic tests/fixtures;
- roadmap/work package/state/claim/changelog/decision documentation.

Use the live PR changed-file list during assurance; do not rely only on this category summary.

## Independent assurance scope

Required verdict:

`ETF_EU_PR91_DONOR_PARITY_ASSURANCE: PASS | FAIL | INDETERMINATE`

Role-B must verify at minimum:
1. exact frozen head and unchanged-head condition;
2. no Weekly FX/product contamination;
3. four protected funded positions including L0CK are represented consistently;
4. retired 50/35/15 and historical CAP01 target weights cannot become current controls;
5. donor 3%/5% cash and ~40% factor rules retain review/disclosure semantics rather than becoming caps;
6. missing current re-underwriting remains unresolved rather than implicit Hold;
7. discovery → UCITS mapping → exact-line pricing → fundability → explicit allocation decision is fail-closed;
8. macro freshness uses donor provenance;
9. funded renderer cannot recreate CAP01/three-position client copy;
10. twenty historical/parallel workflow routes are disabled and the allocator sister-report cannot render parallel client output;
11. candidate workflow cannot self-assure, push candidate output to main or deliver;
12. machine preflight cannot claim independent assurance;
13. controlled transport is the sole active real delivery path and is hash/PASS/commit/principal-authority bound;
14. no portfolio/ledger mutation, broker execution or send occurred on PR #91;
15. final frozen-head CI is green after this handover commit.

## Post-PASS sequence

If and only if the independent verdict is PASS and the reviewed head is unchanged:
1. merge PR #91;
2. run exact-main validation;
3. reconcile project CURRENT_STATE/NEXT_ACTIONS/WORK_CLAIMS/work-package/roadmap/handover/changelog;
4. reconcile central control-plane cache/state;
5. close issue #90 and integration claim only after exact-main evidence;
6. start a separate fresh-report candidate cycle if requested/authorized.

This repair mandate itself does not authorize email delivery or broker execution.

## Handover disposition

`HANDOVER_READY`

Implementation is complete. The next authoritative action is independent role-B assurance on the exact live PR #91 head containing this handover commit.
