# Weekly ETF EU — Realization Runbook V1

**Status:** CANONICAL OPERATING RUNBOOK / ADOPTED  
**Date:** 2026-08-30  
**Repository:** `market-predictions/weekly-etf-eu`  
**Governance repository:** `market-predictions/control-plane`  
**Source design:** `docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md`  
**Adoption:** approved for realization by principal instruction on 2026-08-30; execution remains subject to canonical control-plane governance.

## 0. Executive operating rule

Realization is executed **autonomously, continuously and end-to-end**.

> **Do not stop because a sub-step, commit, test, checkpoint, work package, handover or intermediate milestone completed. Continue immediately with the next lawful and logical step. Chat updates are observability only and must never stall execution. Stop only when the defined end goal is realized or a genuine blocker exists that cannot be resolved within available authority, tools, evidence or governance constraints.**

Default loop:

```text
complete current step
      ↓
validate result
      ↓
retire superseded debt created/exposed by the change
      ↓
record evidence / commit / freeze where required
      ↓
select next lawful step from live state
      ↓
continue immediately
```

## 1. End goal

Weekly ETF EU operates through a Thin Current Kernel:

```text
protected holdings + cash + ledger
        ↓
fresh identity-bound evidence
        ↓
current re-underwriting + broad challengers
        ↓
EU/UCITS fundability + implementation gates
        ↓
explicit model allocation decision
        ↓
portfolio accountability vs stable comparator
        ↓
one frozen per-run review state
        ↓
pure NL/EN client rendering
        ↓
independent exact-head assurance
        ↓
guarded delivery of exact approved artifacts
        ↓
real receipt / closeout evidence
```

At completion: current truth and executors are obvious; live evidence determines volatile state; one current candidate path and sender exist; one per-run review state contains all client-semantic facts; NL/EN Markdown/HTML/PDF are projections of that state; downstream stages cannot change investment semantics after freeze; benchmark/accountability is first-class; retired executors/docs leave active namespaces; no delivery-success claim exists without receipt/manifest evidence.

## 2. Non-negotiable engineering principles

1. First-principles reasoning.
2. Solid but simple.
3. No overengineering.
4. Reuse proven primitives where the problem is genuinely shared.
5. Customer value leads.
6. One current truth per concern.
7. Fail closed on authority and identity.
8. Debt retirement is part of Done.
9. Validators detect; they do not become semantic repair engines.
10. Continuous autonomous execution.

## 3. Authority model

- GitHub is external source of truth; ChatGPT is workbench.
- Keep decision framework, input/state contract, output contract and operational/governance runbook distinct.
- Worker A / `implementation_operations` builds/repairs candidates, tests, retires debt and freezes exact heads. A cannot self-assure or create delivery/broker authority.
- Worker B / `governance_release_assurance` independently reviews one exact frozen head and returns `PASS | FAIL | INDETERMINATE`. B may not repair.
- Any semantic change after B review invalidates the verdict.

## 4. Mandatory startup protocol

Before consequential implementation:

1. Read canonical Control operating method in `market-predictions/control-plane`.
2. Read local `control/SYSTEM_INDEX.md`, `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, then minimum relevant files.
3. Verify volatile reality live: canonical queue/claim, target `main`, open PR/issue lineage, exact candidate head, CI, result/handover/receipt references.
4. Do not reuse stale task/claim/SHA/handover from chat memory.
5. Require lawful claim/`START_PROVEN` where canonical governance requires it.
6. Preserve `principal_manual_relay_count=0` and never hand-edit the canonical dispatch queue.
7. If live state advanced, rebase the plan automatically rather than pausing for routine confirmation.

## 5. Continuous execution protocol

```text
READ LIVE STATE
   ↓
SELECT HIGHEST-PRIORITY LAWFUL TASK
   ↓
CLAIM / START_PROVEN
   ↓
EXECUTE BOUNDED CHANGE
   ↓
TEST + VALIDATE
   ↓
SELF-CRITIQUE AGAINST END GOAL
   ↓
RETIRE SUPERSEDED DEBT
   ↓
RETEST
   ↓
COMMIT / FREEZE / RECORD EVIDENCE
   ↓
HANDOVER OR NEXT TASK
   ↓
RE-READ LIVE STATE
   ↓
CONTINUE
```

Intermediate commits, tests, PRs, freezes, handovers, assurance verdicts, merges, exact-main checks, delivery-authority preparation and chat updates are not stop conditions.

Allowed stop reasons are only `END_GOAL_REACHED` or `GENUINE_UNRESOLVABLE_BLOCKER`. Ordinary bugs, stale docs, merge conflicts, broken imports, missing references and failing tests must be debugged in-scope.

## 6. Change discipline

Prefer narrow vertical slices. A slice normally adds/repairs one current responsibility, proves it, removes/quarantines its predecessor and leaves one clearer authority/executor path.

Historical artifacts have only three states:
1. CURRENT/SUPPORTING ACTIVE;
2. FORENSIC ARCHIVE outside read-first/runtime/workflow namespaces;
3. DELETE (Git history suffices).

Compatibility aliases require canonical replacement, deprecation evidence and bounded sunset.

## 7. Realization sequence

Execute R0 → R1 → R2 → R3 → R4. These are internal exit criteria, not user-approval gates.

### R0 — Truth & Execution Convergence
- Rewrite read-first docs to stable LIVE_FIRST/NARRATIVE_LIGHT semantics.
- Replace US-derived state model with EU persistent/per-run contracts.
- Create one current roadmap pointer; move old roadmaps to explicit archive.
- Build one-off executor reachability inventory from active candidate/delivery workflows.
- Remove `.yml.disabled` from `.github/workflows`; retain only audit-worthy copies in archive.
- Establish one obvious candidate and sender entrypoint.
- Introduce truthful pricing authority naming and bounded old alias sunset.
- Move historical-looking target-weight facts out of current authority surface where safe.
- Close superseded PR/issue lines after live verification.

**Exit:** new worker can identify product truth, candidate executor and sender without archaeology; no investment behavior unintentionally changed.

### R1 — Accountable Decision Kernel
- One stable explicit primary comparator contract.
- Persistent portfolio/comparator accountability history.
- One frozen `review_state_<run_id>.json` with current valuation, funded positions, actions, re-underwriting, challengers, allocation/no-change rationale, accountability, provenance/confidence/unresolved.
- Downstream components may not recalculate or semantically mutate authoritative facts after freeze.
- Deterministic arithmetic/date-alignment/missing-data/contribution/pricing/language-parity tests.

**Exit:** one dated review state answers whether the model added value, why and what deserves capital now.

### R2 — Decision-First Client Surface
First page must expose NAV/invested/cash, weekly action, portfolio vs comparator, active return, contributor/detractor, cash rationale, best challenger, biggest risk and confidence/unresolved. Each funded position gets explicit action, current value/weight, fresh-cash view, rationale, contribution, alternative, invalidation/trigger and confidence. Factory detail moves to appendix.

**Exit:** client understands decision/accountability from first 1–2 pages.

### R3 — Pure Render Convergence

```text
review_state
   ├── report_nl.md
   ├── report_en.md
   ├── report_nl.html
   └── report_en.html

report_nl.html -> report_nl.pdf
report_en.html -> report_en.pdf
```

Renderers localize/style only. Validators detect/fail only. Retire superseded `finalize_*`, `reconcile_*`, `scrub_*`, `synchronize_*`, `fix_*`, duplicate renderers/senders and obsolete preview builders after reference proof. Stop new current writes to legacy output roots; converge toward `state/`, `current/`, `evidence/`, `history/`.

**Exit:** one investment fact changes in one state-building path.

### R4 — Evidence & Epistemic Quality
Add provenance, confidence, unresolved evidence, freshness/expiry and source-quality distinctions inside existing evidence/review-state contracts; no second evidence plane.

**Exit:** material client claims are traceable without parallel authority.

## 8. Mandatory Definition of Done

Every change must satisfy applicable authority, execution, state, output, compatibility, test and documentation criteria from the architecture. In particular: one current authority/executor; persistent vs per-run truth separated; NL/EN/HTML/MD/PDF reconcile; PDF from approved HTML; delivery sends frozen artifacts; old aliases have sunset; negative tests block retired semantics; current docs are updated and stale current-looking predecessors leave active namespaces.

## 9. Governed candidate / assurance / integration sequence

Worker A:
1. verify live lawful work state;
2. implement bounded change;
3. targeted tests + repository/product validators;
4. debt-retirement pass + retest;
5. stable docs/decision log updates;
6. commit/freeze exact head;
7. record exact base/head/evidence and durable handover;
8. do not self-assure.

Worker B:
1. independently verify task/repo/base/head;
2. review exact frozen candidate and supporting evidence;
3. assess semantics, authority boundaries, regressions and debt retirement;
4. return `PASS | FAIL | INDETERMINATE` and durable evidence;
5. do not repair.

After PASS: verify unchanged head, governed integration, exact-main validation, then continue. After FAIL: bounded repair lineage, new exact head and fresh B review. INDETERMINATE is an execution/evidence state, never PASS.

## 10. Progress reporting

```text
[ETF-EU] <timestamp Amsterdam>
Status: <active slice/task>
Changed: <material result>
Evidence: <test/commit/PR/result refs>
Risk/blocker: <none or exact issue>
Continuing now: <next action already underway>
```

Updates document motion; they do not create a pause.

## 11. Session close rule

Before unavoidable session close: finish safe atomic mutation, persist authoritative work, finalize/release claims correctly, record concise durable summary, update stable docs only if stable content changed, record stable decisions in `control/DECISION_LOG.md`, record exact next lawful action from live state, and ensure continuation requires no chat archaeology.

Only `END_GOAL_REACHED` or `GENUINE_UNRESOLVABLE_BLOCKER` is a valid terminal reason.
