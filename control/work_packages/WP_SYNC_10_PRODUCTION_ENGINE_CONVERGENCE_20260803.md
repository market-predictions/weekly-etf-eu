# WP-SYNC-10 — Production engine convergence and premium client-report promotion

**Date opened:** 2026-08-03  
**Repository:** `market-predictions/weekly-etf-eu`  
**Branch:** `sync/wp10-production-engine-convergence`  
**Status:** claimed and in progress  
**Claimed by:** ChatGPT autonomous development session

## Current issue

The repository currently contains two mature but separate report paths:

1. the routine client-grade v2 production renderer; and
2. the merged donor-synchronization / policy-allocator sister-report engine.

The routine renderer has a premium visual surface, but its content layer still contains hardcoded lane definitions, incumbent names, candidate labels and large string-replacement tables. It can therefore drift from the merged donor, UCITS mapping, allocator and evidence contracts.

The synchronized sister report is state-driven and contract-validated, but remains labelled and operated as shadow output and is not the routine production renderer.

## Objective

Create one production-candidate report path that:

- uses the merged Weekly ETF donor synchronization engine;
- uses the official EU portfolio and valuation history as state authority;
- uses ISIN-first UCITS mappings and exact trading-line identifiers;
- uses allocator and evidence results for all position, candidate, blocker and action surfaces;
- preserves the premium Dutch-primary / English-companion look and feel;
- renders every funded position and every promoted candidate consistently;
- keeps blocked target capacity in cash;
- creates no portfolio, ledger, execution or delivery authority.

## Four-layer scope

### 1. Decision framework

- Separate current holdings, feasible shadow targets, blocked target capacity and future candidates.
- Show all official funded positions exactly once.
- Show all promoted donor exposures and their current EU implementation status.
- Never convert donor target presence, report prose, or a shadow target into add authority.
- Preserve the WP-SYNC-09 blocked Stage-1 decision until evidence and donor authority change.

### 2. Input/state contract

Authoritative inputs:

```text
official_portfolio=output/etf_eu_portfolio_state.json
official_valuation_history=output/etf_eu_valuation_history.csv
shared_strategy_state=current pinned donor build
shared_portfolio_target=current pinned donor build
strategy_sync_shadow=run-scoped synchronized exposure state
policy_allocator=run-scoped policy allocator output
wp09_evidence=latest accepted fresh evidence receipt
ucits_registry=merged ISIN-first synchronization registry
```

Rules:

- Portfolio quantities and cash come only from official EU state.
- Donor state provides strategy context, not EU execution authority.
- UCITS identity is ISIN plus exact trading line.
- Portfolio label `LOCK` and Xetra symbol `L0CK` remain explicitly distinct.
- Cached connectivity may be disclosed but may not be promoted to activation-grade evidence.
- Previous report prose is not an input.

### 3. Output contract

Generate Dutch-primary and English-companion HTML/PDF reports from one normalized production-convergence state.

Required surfaces:

1. premium decision cockpit;
2. official portfolio and cash;
3. current regime and policy context;
4. synchronized opportunity radar;
5. risks and invalidations;
6. portfolio development and contribution;
7. allocation map;
8. second-order effects;
9. exact UCITS candidate and pricing/evidence table;
10. verification funnel;
11. current-position review;
12. replacement and rotation analysis;
13. final action table;
14. proposed changes / explicit no-trade result;
15. current positions and cash;
16. next-run inputs and disclaimer.

The client surface must not contain:

- `shadow report`, `shadow output` or internal authority terminology;
- raw exposure IDs or blocker enums;
- stale hardcoded satellite labels;
- U.S.-listed ETFs represented as EU investable instruments;
- action claims inconsistent with the policy allocator;
- portfolio mutation or delivery claims.

### 4. Operational runbook

- Build current donor and synchronized artifacts in an isolated workflow.
- Build a production-convergence state adapter.
- Render bilingual premium HTML/PDF outputs.
- Run machine validation and full PDF layout validation.
- Compare official portfolio and ledger hashes before and after.
- Upload artifacts only.
- Do not send email and do not mutate official state.

## Upstream reuse decision

Closest mature upstream concepts inspected in `market-predictions/weekly-etf`:

- runtime-derived report state;
- cockpit-first premium hierarchy;
- action and portfolio surfaces derived from state rather than report prose;
- equity history and contribution truth;
- client-language leakage gates;
- strict HTML/PDF output validation.

Adaptation decision:

```text
port state-driven cockpit and output-contract behavior
retain EU synchronized sister-report section breadth
replace U.S. instrument assumptions with ISIN-first UCITS authority
```

## Initial implementation files

Planned additions:

```text
runtime/build_etf_eu_production_convergence_state.py
runtime/render_etf_eu_production_converged_report.py
tools/validate_etf_eu_production_convergence_state.py
tools/validate_etf_eu_production_converged_report.py
.github/workflows/validate-etf-eu-production-convergence.yml
```

Planned integration changes:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/CHANGELOG.md
```

Legacy files remain available during validation. They are not deleted until the converged path proves complete parity.

## Acceptance contract

```text
funded_position_count=3
funded_tickers=VWCE,EUNA,SXR8
promoted_exposure_count=6
mapped_promoted_exposure_count=6
unmapped_promoted_exposure_count=0
stage_1_decision=blocked
stage_1_activation_authorized=false
portfolio_mutation=false
ledger_write=false
execution_authority=false
production_delivery_authority=false
executable_trade_intents=[]
client_shadow_language_absent=true
raw_internal_tokens_absent=true
all_required_sections_present=true
nl_pdf_valid=true
en_pdf_valid=true
protected_state_unchanged=true
```

## Non-goals

- no Stage-1 or Stage-2 activation;
- no official portfolio or ledger mutation;
- no broker execution;
- no email delivery;
- no weakening of current market-evidence or donor fresh-add gates;
- no forced deployment of capital where evidence or authority is absent.

## Initial next actions

1. Build the synchronized production-convergence state.
2. Render Dutch and English production-candidate reports.
3. Add strict state and client-surface validators.
4. Run the isolated workflow and repair concrete defects.
5. Perform complete visual review.
6. If green, merge the reusable production-convergence capability and define the separate guarded promotion/delivery package.
