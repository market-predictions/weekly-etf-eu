# ETF EU Lane Discovery Contract

## Purpose

This contract ports the mature Weekly ETF discovery behavior into the EU/UCITS product without importing U.S. investability assumptions.

The Structural Opportunity Radar must come from broad internal discovery, current donor opportunity evidence, UCITS mapping status, current pricing/fundability evidence, portfolio gaps, challenger rotation and liquidity/relative-strength context where available.

A missing exact UCITS implementation blocks **funding**, not **research coverage**.

## Five-layer placement

1. **Decision framework** — broad discovery and lane ranking before capital decisions.
2. **Input/state contract** — donor lane evidence + EU discovery universe + exact UCITS mappings + pricing + portfolio state.
3. **Output contract** — compact client radar plus machine-readable assessed/omitted lanes.
4. **Operational runbook** — donor discovery → EU mapping → pricing/fundability → re-underwriting → report state.
5. **Governance** — fail closed if U.S. proxy, stale shadow gate or incomplete mapping becomes funding authority.

## EU discovery authority order

Use:

1. current Weekly ETF donor lane/opportunity artifact as research context;
2. `config/etf_eu_discovery_universe.yml` for persistent EU breadth/mapping memory;
3. current exact mapping/identity evidence, including `config/ucits_symbol_registry.yml` and current mapping artifacts;
4. current UCITS completed-close pricing evidence;
5. `output/etf_eu_portfolio_state.json` for actual holdings/cash;
6. current `output/etf_eu_recommendation_scorecard.csv` for re-underwriting memory;
7. prior EU lane/report artifacts for continuity only.

Donor target weights and U.S.-listed tickers do not create EU allocation authority.

## Required breadth behavior

Each current run should assess all required breadth buckets declared in `config/etf_eu_discovery_universe.yml`, matching the mature donor breadth model:

- ai_digital_infrastructure
- defense_resilience
- grid_power_electrification
- uranium_nuclear
- agriculture_food_security
- water
- china
- india_regional_industrialization
- biotech_healthcare_innovation
- fintech_financial_infrastructure
- robotics_automation
- critical_minerals_materials

The run should construct 10–15 candidate lanes where current donor evidence allows, include at least four challengers, and promote roughly 5–8 highest-ranked lanes to the live radar when evidence quality supports it.

These are research/discovery completeness targets, not portfolio position-count or funding rules.

## Proxy → UCITS rule

For every lane distinguish:

```text
research proxy / donor vehicle
EU mapping status
exact UCITS candidate
fundability status
```

Allowed mapping states include:

```text
funded_exact_ucits_line
exact_ucits_mapping_available
exact_ucits_mapping_available_but_fresh_fundability_evidence_required
mapping_required
policy_review_required
```

Rules:

- a U.S. ETF can rank a research lane but can never be the funded EU instrument;
- `mapping_required` remains visible in internal breadth evidence and is never auto-omitted merely because funding is impossible;
- exact ISIN/share class/venue/trading line/currency must be resolved before model funding;
- UCITS/PRIIPs/KID and completed-close gates remain independent of discovery score;
- a priced candidate is not automatically fundable;
- broker-specific account permission is not a model-investability discovery gate.

## Challenger discipline

A current run should include at least four challengers when feasible, including new or previously omitted buckets.

Challengers should carry:

- novelty status;
- current mapping status;
- current price status;
- relative-strength/liquidity evidence where available;
- portfolio differentiation;
- rejection/blocker reason;
- what would change the status.

A challenger with incomplete EU mapping remains `research_only_mapping_required`, not silently dropped.

## Relative-strength and liquidity behavior

Port donor behavior where data exists:

- 1m/3m returns;
- trend quality;
- drawdown;
- volatility;
- relative strength versus a relevant benchmark/proxy;
- average traded value / spread / tradability evidence;
- direct comparison versus a holding or alternative when relevant.

Historical transition thresholds do not become current hard eligibility limits automatically. Current evidence may trigger a liquidity/concentration review; a numerical hard threshold requires current authority.

## Two-pass pricing behavior

The intended current sequence is:

```text
funded-holdings pricing
→ broad donor discovery
→ EU mapping status resolution
→ targeted pricing for top mapped challengers
→ fundability classification
→ final lane ranking/re-underwriting
→ normalized report state
```

Failure to price an unfunded challenger must not weaken funded-holdings valuation. It limits that challenger to research/monitoring until sufficient evidence exists.

## Machine-readable lane fields

Every assessed EU lane should expose at least:

- lane_name
- taxonomy_tag
- bucket
- donor_proxy_or_reference
- proxy_authority
- structural/persistence/macro/timing/implementation scores when available
- current donor rank/score when available
- challenger / novelty status
- mapping_status
- candidate ISIN/ticker/venue/currency when mapped
- ucits_status
- priips_kid_status
- exact_line_status
- current_price_status
- liquidity/tradability evidence
- fundability_status
- portfolio_gap / differentiation
- promoted_to_live_radar
- rejection_or_blocker_reason
- what_would_change

Missing evidence must be explicit rather than fabricated.

## Current Stage-1 boundary

The historical Stage-1 candidate set (`ai_compute_infrastructure`, `cyber_security`) is activation provenance only.

```text
historical_stage1_allowlist_is_current_discovery_gate=false
historical_stage1_allowlist_is_current_allocation_gate=false
```

Broad current discovery must not be filtered down to that historical set.

## Output contract

The client report remains selective. Broad assessment evidence belongs primarily in machine artifacts and compact omitted/monitoring proof.

Client language must distinguish:

- current funded position;
- current mapped/fundable candidate;
- mapped but evidence-incomplete candidate;
- research-only proxy or mapping gap.

## What this layer is not

- not automatic trading;
- not permission to fund every mapped UCITS ETF;
- not a source of hard cash/turnover/theme caps;
- not permission to reuse stale donor target weights;
- not a reason to downgrade EU identity/KID/exact-line controls.

## Definition of done

Discovery is donor-comparable when broad donor research coverage can survive the EU translation step, exact UCITS mappings are tracked separately from research proxies, top mapped challengers receive current pricing/fundability review, and no missing mapping or old Stage-1 gate silently shrinks the research universe.
