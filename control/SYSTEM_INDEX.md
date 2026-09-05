# Weekly ETF EU Review OS — System Index

This is the stable first entry point for serious work on `market-predictions/weekly-etf-eu`.

## Product mission

Weekly ETF EU is a weekly EU-investable capital-decision and accountability system. It answers where the model portfolio stands, whether the process is adding value versus a stable investable comparator, which funded holdings still deserve capital, which alternatives are better, what should change now, and why. The premium NL/EN report is the client interface to that decision and evidence.

Canonical product architecture:
- `docs/architecture/WEEKLY_ETF_EU_PRODUCT_ARCHITECTURE_V2.md`
- `docs/runbooks/WEEKLY_ETF_EU_REALIZATION_RUNBOOK_V1.md`
- `control/DECISION_LOG_20260831_ARCHITECTURE_V2.md`

The upstream `market-predictions/weekly-etf` repository is a donor for proven primitives and behavior. It is never authority for EU holdings, prices, recipients, trading lines, allocation, delivery or workflow state.

## Mandatory session start

For meaningful ETF-EU architecture, debugging, prompt, script, workflow, report or delivery work:

1. read the canonical operating method in `market-predictions/control-plane`;
2. read `control/SYSTEM_INDEX.md`;
3. read `control/CURRENT_STATE.md`;
4. read `control/NEXT_ACTIONS.md`;
5. read `control/PRICING_AUTHORITY_CURRENT.md` for pricing/report/fundability work;
6. inspect live canonical queue/claim state and target-repository branch/PR/issue evidence where the work is consequential;
7. read only the minimum relevant execution/governance files.

**LIVE_FIRST rule:** volatile facts such as current `main` SHA, active issue/PR, claim owner, candidate head, CI result and delivery receipt are resolved from live GitHub/control-plane evidence. They are deliberately not duplicated here as “current state”.

Historical issues, work packages, reports, archived workflows and metadata are provenance only. They never override later merged code, protected machine state or current read-first authority.

## Four product layers + governance boundary

Always keep distinct:

1. **Decision framework** — what deserves capital and why.
2. **Input/state contract** — protected holdings/cash/ledger plus fresh identity-bound evidence.
3. **Output contract** — one frozen per-run review state and pure NL/EN projections.
4. **Operational runbook** — deterministic generation, validation, persistence and delivery mechanics.

Independent release assurance and guarded delivery protect the boundary around these layers; they do not create investment semantics.

## Cross-project governance authority

Shared governance lives in `market-predictions/control-plane`, including:
- `control/CROSS_PROJECT_PRINCIPAL_AGENT_OPERATING_CHARTER_V1.md`
- `control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md`
- `control/WORK_CLAIM_AND_BRANCH_LIFECYCLE_STANDARD_V1.md`
- `control/CONTROL_QUEUE_PROTOCOL_V1.md`

Local compatibility copies are migration provenance, not shared authority.

### Worker separation

- Worker A / `implementation_operations` builds or repairs one candidate and may not self-assure.
- Worker B / `governance_release_assurance` independently reviews one exact frozen candidate head and may not repair it.
- Semantic candidate changes invalidate prior assurance.
- `principal_manual_relay_count=0` remains the orchestration target.

## Canonical persistent EU state

Authoritative persistent domain truth:
- `output/etf_eu_portfolio_state.json`
- `output/etf_eu_trade_ledger.csv`
- `output/etf_eu_valuation_history.csv`
- `output/etf_eu_accountability_history.csv`
- `output/etf_eu_recommendation_scorecard.csv`
- `config/ucits_symbol_registry.yml`

Related authority contracts:
- `control/ETF_EU_ALLOCATION_AUTHORITY_V1.md`
- `control/ETF_EU_DISCOVERY_FUNDABILITY_CONTRACT_V1.md`
- `control/UCITS_ETF_REVIEW_CONTRACT_V1.md`
- `control/UCITS_INVESTABILITY_RULES.md`
- `control/UCITS_SYMBOL_REGISTRY_CONTRACT.md`
- `control/PRICING_AUTHORITY_CURRENT.md`

Authority order for current allocation:

```text
explicit current allocation decision
> protected portfolio state + trade ledger
> current completed-close valuation + current re-underwriting evidence
> current donor opportunity evidence mapped to verified UCITS lines
> historical strategy/shadow context
```

Historical activation/transition target values are audit context, never implicit current allocation authority.

## Per-run semantic authority

The Thin Current Kernel lives under `runtime/current/` and produces one immutable/frozen per-run review state as the only client-semantic authority after build. It is derived from protected persistent state plus current evidence.

After freeze, renderers/validators/delivery may not:
- recalculate NAV into a different value;
- choose a different authoritative price;
- change a funded-position action;
- change allocation semantics;
- rewrite comparator performance;
- manufacture missing evidence.

A semantic change requires a new review state and new candidate head.

Current package namespaces:

```text
output/current/
output/history/<report_date>/<run_id>/
output/evidence/<run_id>/
```

## Current pricing authority — stable policy

Canonical human-readable summary: `control/PRICING_AUTHORITY_CURRENT.md`.

Stable rule:
- exact canonical UCITS trading-line identity is mandatory;
- one qualified statically bound primary provider with the exact requested completed-session close may be valuation-grade as `fresh_exact_unverified`;
- a correctly bound exact same-date verifier within tolerance upgrades to `fresh_exact_verified`;
- stale/missing/unbound verifier evidence does not block a valid exact primary;
- accepted exact same-date disagreement fails closed;
- stale-only pricing, missing exact requested-date close or primary identity/binding failure remains fail-closed;
- selected valuation price is the authoritative primary close, not a median blend.

The retired statement “every funded line requires two live same-date providers” is historical only.

## EU configuration

Current identity/investability/discovery configuration includes:
- `config/ucits_symbol_registry.yml`
- `config/ucits_benchmark_proxy_map.yml`
- `config/nl_client_investability_rules.yml`
- `config/etf_eu_discovery_universe.yml`

Historical/non-executable allocation context must remain explicitly non-current.

## Current operational entrypoints

Authoritative workflow index: `control/ETF_EU_WORKFLOW_AUTHORITY_INDEX_V1.md`.

### Candidate build
`.github/workflows/run-weekly-etf-eu-routine.yml`

Candidate build:
- refuses `main`;
- may build, validate and persist candidate evidence on its candidate branch;
- cannot self-assure, merge, create delivery authority, send email or execute broker actions.

### Guarded delivery
`.github/workflows/send-weekly-etf-eu-controlled-transport.yml`

Guarded delivery is a separate main-only boundary. It sends exact approved artifacts without re-rendering and requires independent assurance plus separate current send authority. SMTP success is not inbox receipt; delivery closes only on positive receipt/manifest evidence.

### Runtime boundary

The only allowed top-level runtime namespace is:

```text
runtime/__init__.py
runtime/adapt_weekly_etf_macro_for_eu.py
runtime/current/
runtime/send_etf_eu_controlled_report.py
runtime/write_etf_eu_delivery_evidence.py
runtime/check_etf_eu_delivery_receipt.py
```

`tools/validate_etf_eu_current_reachability.py` fails closed if parallel executors reappear.

## Donor reuse rule

Before porting donor code:
1. prove the underlying problem is genuinely shared;
2. reuse only if the donor primitive remains simpler than rebuilding;
3. never import donor state/recipient/workflow authority;
4. wrap with EU identity/investability/pricing gates;
5. identify which EU duplicate becomes removable.

A port that removes nothing is presumptively adding a parallel path.

## Non-negotiable controls

- ISIN-first/trading-line identity; ticker alone is insufficient.
- No U.S.-listed ETF presented as Dutch/EU investable holding.
- No funding before investability, pricing, re-underwriting and explicit allocation gates.
- No protected portfolio/ledger mutation without explicit current allocation authority.
- No current Hold/Add/Reduce inferred from old targets/actions/report prose.
- No donor review threshold treated as allocation cap.
- No machine/CI preflight represented as independent assurance.
- No generation/SMTP represented as delivery success.
- Exact artifacts are bound before guarded transport.
- Missing/contradictory authority evidence fails closed.
- Do not accumulate consequential work on a materially stale claim/integration line.

## Volatile operating state

This file intentionally contains **no current SHA, issue, PR, claim, candidate or lifecycle label**. Resolve those facts live under the startup protocol. `control/CURRENT_STATE.md` explains the stable state topology; `control/NEXT_ACTIONS.md` defines priority policy rather than a manually synchronized task list.
