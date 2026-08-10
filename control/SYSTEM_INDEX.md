# Weekly ETF EU Review OS — System Index

This file is the first entry point for serious work on `market-predictions/weekly-etf-eu`.

## Product purpose

```text
Dutch/EU-client ETF review using UCITS ETFs as investable instruments.
```

The upstream `market-predictions/weekly-etf` repository is a donor for mature decision/state patterns. It is not authority for EU holdings, recipients, trading lines, allocation decisions or delivery decisions.

## Mandatory session start

Read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/WORK_CLAIMS.json`
5. the active/superseding handover record referenced by the claim registry, when present
6. `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`
7. `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`
8. the minimum relevant execution files

Before continuing consequential work, reconcile the active claim against live GitHub branch, target, dependency, PR and handover state under the canonical control-plane lifecycle standard. Do not continue accumulating on a materially stale integration line.

## Five-layer operating model

Always distinguish:

1. **Decision framework** — which UCITS instruments deserve capital.
2. **Input/state contract** — authoritative instruments, prices, holdings, cash and ledger facts.
3. **Output contract** — Dutch-primary and English-companion report behavior.
4. **Operational runbook** — generation, validation, persistence, transport and closeout.
5. **Governance and release assurance** — independent proof that the complete requested outcome was achieved.

## Cross-project governance authority

Canonical shared governance and claim/branch standards live in:

`market-predictions/control-plane`

Relevant standards:
- `control/CROSS_PROJECT_PRINCIPAL_AGENT_OPERATING_CHARTER_V1.md`
- `control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md`
- `control/WORK_CLAIM_AND_BRANCH_LIFECYCLE_STANDARD_V1.md`

Local compatibility copies are migration provenance, not current shared authority.

## Two-role governance model

The project has one user-facing coordinator and two internally separated roles:

```text
implementation_operations
governance_release_assurance
```

Role A builds/repairs a candidate. Role B independently reviews one exact frozen candidate head. Role A may not self-certify. Role B may not mutate the reviewed candidate.

Project governance authority:
- `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`
- `control/ETF_EU_TWO_ROLE_GOVERNANCE_MODEL_V1.md`
- `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`
- `control/ETF_EU_GOVERNANCE_CHANGELOG.md`
- `control/WORK_CLAIMS.json`

Historical machine tooling retains compatibility filenames:
- `tools/build_etf_eu_release_assurance.py`
- `tools/validate_etf_eu_release_assurance.py`
- `.github/workflows/validate-etf-eu-release-assurance.yml`

Their current authority is **machine release-evidence preflight only**. They cannot issue an independent assurance verdict, merge authority or delivery authority.

## Work-claim and handover authority

Machine-readable claim registry:

`control/WORK_CLAIMS.json`

Durable ownership/lineage handovers:

`handover/`

Rules:
- detect stale/orphaned claims without principal prompting;
- one active release-integration claim per release line;
- merged/closed PRs may not leave overlapping active claims;
- superseded branches are read-only evidence donors;
- generated reports/CI retriggers may not prolong a materially stale line;
- roadmap/current-state must point at the surviving claim;
- every handover ends `CLOSE`, `TRANSFER` or `SUPERSEDE`.

## Canonical EU decision and state authority

- `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`
- `control/ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1.md`
- `control/UCITS_ETF_REVIEW_CONTRACT_V1.md`
- `control/UCITS_INVESTABILITY_RULES.md`
- `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md`
- `output/etf_eu_portfolio_state.json`
- `output/etf_eu_trade_ledger.csv`
- `output/etf_eu_valuation_history.csv`
- `output/etf_eu_recommendation_scorecard.csv`

Authority order for current allocation:

```text
explicit current allocation decision
> protected portfolio state + trade ledger
> current completed-close valuation + current recommendation evidence
> current donor opportunity state mapped to verified UCITS lines
> historical strategy/shadow context
```

Historical CAP01/transition target values are audit context, not current allocation authority.

## Canonical EU configuration

- `config/ucits_symbol_registry.yml` — identity/investability authority only; not funded-state authority
- `config/ucits_benchmark_proxy_map.yml`
- `config/nl_client_investability_rules.yml`
- `config/etf_eu_discovery_universe.yml`

Historical/non-executable allocation context:
- `config/etf_eu_transition_policy_v1.yml`
- `config/etf_eu_target_allocation.yml`

Both are explicitly non-current authority.

## Canonical output behavior

Current state is normalized before rendering by:
- `runtime/apply_etf_eu_donor_parity_contract.py`

Funded client rendering:
- `runtime/render_etf_eu_client_grade_v2_funded.py`

Rules:
- all funded positions must be present, including L0CK;
- no historical strategic/phase target may appear as a current target;
- no retired 50/35/15 or fixed-reserve policy may appear as current control;
- missing current re-underwriting is `UNRESOLVED`, not implicit Hold;
- NL and EN are produced from one normalized state.

## Canonical operational topology

Authoritative index:

`control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`

### Candidate build

`.github/workflows/run-weekly-etf-eu-routine.yml`

This workflow:
- refuses `main`;
- builds and machine-validates a candidate;
- may persist generated candidate evidence only to its candidate branch;
- cannot self-assure;
- cannot merge;
- cannot create delivery authority;
- cannot send email;
- cannot execute broker actions.

### Independent assurance

After the candidate is frozen, a separate `governance_release_assurance` reviewer returns:

`PASS | FAIL | INDETERMINATE`

on the exact head. Any semantic candidate change invalidates the verdict.

### Merge / exact-main

Merge is permitted only after independent PASS and unchanged reviewed head. Exact-main validation follows merge.

### Guarded delivery

`.github/workflows/send-weekly-etf-eu-controlled-transport.yml`

This is the sole active real delivery workflow. It is main-only and requires a committed guarded-delivery authority binding:
- exact independently assured candidate head;
- approved report commit in main lineage;
- independent PASS evidence reference;
- separate principal guarded-send authorization;
- exact NL/EN MD/HTML/PDF paths and SHA-256 hashes.

It sends the approved artifacts without re-rendering. SMTP success is not inbox receipt. Delivery closes only on positive independent receipt/attachment evidence.

Historical activation/send/repair/preview workflows are retained only as `.yml.disabled` audit history.

## Upstream-first reuse rule

Before creating or materially changing an EU workflow, runtime script, validator, renderer or control contract:

1. inspect the closest mature upstream implementation;
2. choose port, adapt, wrap or intentional divergence;
3. record the decision;
4. never import U.S. state or recipient authority as EU authority;
5. do not copy a donor operational weakness merely to achieve superficial symmetry.

## Non-negotiable controls

- Use ISIN-first identity; ticker alone is insufficient.
- Do not present U.S.-listed ETFs as Dutch/EU investable holdings.
- Do not fund an instrument before investability, pricing, re-underwriting and explicit allocation gates pass.
- Do not mutate protected portfolio state or ledger without explicit allocation authority.
- Do not infer current Hold/Add/Reduce from historical targets, old actions or report prose.
- Do not turn donor review/disclosure thresholds into allocation caps.
- Do not claim independent assurance from machine/CI evidence.
- Do not claim production delivery from generation, validation or SMTP success alone.
- Bind exact approved artifacts before guarded transport.
- Require independent receipt evidence before `DELIVERY_CONFIRMED`.
- Treat missing or contradictory evidence as a blocker.
- Do not continue implementation/release accumulation on a materially stale claim branch.

## Current operating mode

```text
DONOR_PARITY_RECONCILIATION_WITH_INDEPENDENT_RELEASE_ASSURANCE
```

Current direction:

```text
PR91 implementation convergence
→ final exact-head CI
→ frozen implementation handover
→ independent governance_release_assurance
→ merge if PASS and unchanged
→ exact-main validation
→ issue/claim/project/control-plane closeout
→ separate fresh-report production cycle
→ separately authorized guarded transport
→ independent receipt verification
```
