# ETF EU Cockpit PDF Readiness Gap Closure Plan V1

## Purpose

This plan converts the ETF-EU-WP15W readiness audit blockers into a non-executing closure plan.

It defines what evidence is missing, where that evidence should come from in a later package, what future validators must check, and what authority is required before any evidence can be collected or surfaced.

This plan does **not** collect evidence, fetch pricing, mutate portfolio state, promote candidates, create funding authority, create valuation-grade authority, grant client-grade approval, grant delivery-preflight authority, create delivery artifacts, rebuild the PDF, or change recommendation logic.

## Source audit

```text
source_work_package=ETF-EU-WP15W
source_readiness_audit_artifact=output/client_surface/etf_eu_cockpit_pdf_readiness_gate_implementation_audit_20260703_000000.json
client_grade_readiness_audit_result=fail_blocked_by_missing_evidence
readiness_audit_status=completed_with_blocking_gaps
```

## Closure principle

WP15X is a planning and contract package only.

```text
gap_closure_plan_status=non_executing_plan_created
execution_performed=false
client_grade_claim=false
client_grade_enough_for_delivery_preflight_discussion=false
delivery_ready=false
```

Any gap requiring data retrieval, pricing, valuation, portfolio changes or delivery requires a later explicit authority package.

## Decision framework gap

### thesis_and_invalidation_present_for_funded_holdings_or_proposed_candidates

```text
layer=decision_framework
current_status=fail
future_package_type=manual_review
execution_authority_required=explicit_later_authority_required
```

Why it blocks client-grade:

```text
The current PDF has candidate reason/condition snippets, but not a full candidate-level thesis, invalidation trigger, evidence horizon and authority-safe decision status for each candidate.
```

Required evidence:

```text
candidate-level thesis
invalidation trigger
evidence horizon
decision status: review/watch/block/promote
explicit no-funding marker unless later authority exists
```

Expected source contract or file:

```text
future evidence acquisition contract
future candidate thesis evidence artifact
output/etf_eu_recommendation_scorecard.csv, if later authorized
```

Future validator expectation:

```text
every candidate row has thesis and invalidation text
no candidate is promoted without authority
no candidate is presented as funded unless funding_authority=true in a later authorized package
```

Risk if skipped:

```text
The cockpit may look visually ready while still lacking the decision rationale and invalidation discipline required for a client-grade investment review.
```

## Input/state contract gaps

The following input/state gaps require later evidence acquisition or data-contract work. WP15X does not collect that evidence.

### isin_first_identity_present

```text
layer=input_state_contract
current_status=fail
future_package_type=data_contract
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
authoritative ISIN per candidate and per investable row
explicit non-UCITS or policy status where no UCITS ISIN applies
```

Expected source contract or file:

```text
config/ucits_symbol_registry.yml
config/ucits_benchmark_proxy_map.yml
future evidence acquisition artifact
```

Future validator expectation:

```text
every candidate or investable row is ISIN-first or explicitly blocked as not an investable UCITS ETF
```

Risk if skipped:

```text
A ticker-only or incomplete row can be confused with an investable Dutch/EU UCITS holding.
```

### trading_currency_present

```text
layer=input_state_contract
current_status=fail
future_package_type=data_contract
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
trading currency for each exchange trading line
```

Expected source contract or file:

```text
config/ucits_symbol_registry.yml
future evidence acquisition artifact
```

Future validator expectation:

```text
every investable row has a trading_currency field
```

Risk if skipped:

```text
Currency exposure and execution assumptions remain ambiguous.
```

### pricing_symbol_present

```text
layer=input_state_contract
current_status=fail
future_package_type=data_contract
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
authoritative pricing symbol per exchange line
pricing symbol namespace/source rule
```

Expected source contract or file:

```text
config/ucits_symbol_registry.yml
future pricing evidence contract
```

Future validator expectation:

```text
every investable row has a pricing_symbol separate from display ticker when required
```

Risk if skipped:

```text
The report may show an exchange ticker without a deterministic pricing lookup contract.
```

### latest_close_date_present

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
latest close date per pricing symbol
pricing freshness status
```

Expected source contract or file:

```text
output/etf_eu_valuation_history.csv
future pricing evidence artifact
```

Future validator expectation:

```text
every investable row has latest_close_date and freshness status from an authorized pricing run
```

Risk if skipped:

```text
The PDF cannot support valuation-grade or delivery-preflight discussion.
```

### latest_close_present

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
latest close value per pricing symbol
currency-aware close value
```

Expected source contract or file:

```text
output/etf_eu_valuation_history.csv
future pricing evidence artifact
```

Future validator expectation:

```text
every investable row has latest_close from an authorized pricing run
```

Risk if skipped:

```text
The report cannot claim current valuation evidence.
```

### pricing_source_present

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
pricing source per pricing symbol
source timestamp or run id
```

Expected source contract or file:

```text
future pricing evidence contract
output/etf_eu_valuation_history.csv
```

Future validator expectation:

```text
every pricing row has pricing_source and pricing_source_run_id or equivalent lineage
```

Risk if skipped:

```text
Freshness and lineage cannot be audited.
```

### ter_or_cost_status_present

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
TER or explicit cost-status field per candidate
source date or document reference
```

Expected source contract or file:

```text
future fund facts/KID evidence artifact
config/nl_client_investability_rules.yml
```

Future validator expectation:

```text
every candidate has ter_or_cost_status populated or explicitly review-needed
```

Risk if skipped:

```text
Cost suitability remains incomplete.
```

### replication_method_present_or_explicitly_unknown

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
replication method per ETF or explicit unknown marker
```

Expected source contract or file:

```text
future fund facts/KID evidence artifact
config/ucits_symbol_registry.yml
```

Future validator expectation:

```text
every ETF candidate has replication_method or explicitly_unknown
```

Risk if skipped:

```text
Physical/synthetic risk remains hidden.
```

### distribution_policy_present_or_explicitly_unknown

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
distribution policy per ETF or explicit unknown marker
```

Expected source contract or file:

```text
future fund facts/KID evidence artifact
config/ucits_symbol_registry.yml
```

Future validator expectation:

```text
every ETF candidate has distribution_policy or explicitly_unknown
```

Risk if skipped:

```text
Income/accumulation assumptions remain ambiguous.
```

### hedged_unhedged_status_present_or_explicitly_unknown

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
hedged/unhedged status per ETF or explicit unknown marker
```

Expected source contract or file:

```text
future fund facts/KID evidence artifact
config/ucits_symbol_registry.yml
```

Future validator expectation:

```text
every ETF candidate has hedged_unhedged_status or explicitly_unknown
```

Risk if skipped:

```text
Currency hedge assumptions remain invisible.
```

### liquidity_spread_evidence_present_or_review_needed

```text
layer=input_state_contract
current_status=blocked
future_package_type=evidence_collection
execution_authority_required=explicit_later_authority_required
```

Required evidence:

```text
liquidity/spread evidence or explicit review-needed marker
source and freshness status
```

Expected source contract or file:

```text
future liquidity/spread evidence artifact
output/etf_eu_recommendation_scorecard.csv, if later authorized
```

Future validator expectation:

```text
every candidate has liquidity_spread_evidence or explicit review_needed status
```

Risk if skipped:

```text
Execution quality and investability remain unverified.
```

## Output contract closure plan

```text
no_output_contract_gap_requiring_closure=true
```

Later validation expectation:

```text
Once evidence gaps are closed, the PDF must expose the new evidence without clipping, overlap, raw control noise, unreadable small text or confusion between candidates and funded holdings.
```

## Operational runbook closure plan

```text
no_operational_runbook_gap_requiring_closure=true
```

Future validator expectations:

```text
targeted validator exists for evidence completeness
targeted pytest exists for evidence completeness
no live data fetch occurs without later explicit authority
no portfolio mutation occurs without later explicit authority
no delivery manifest or receipt exists without later explicit authority
```

## Recommended next package

```text
ETF-EU-WP15Y — ETF EU cockpit PDF readiness evidence acquisition contract, no delivery
```

Purpose:

```text
Define the precise evidence acquisition contract for UCITS identity, pricing freshness, TER, replication, distribution, hedging, liquidity/spread and thesis/invalidation evidence before any later authorized data collection package.
```
