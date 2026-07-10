# Weekly ETF EU Review OS — Next Actions

Current priority: **ETF-EU-MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP**.

## Latest completion

```text
work_package_id=ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE
status=completed_fresh_package_readiness_gate_passed
source_work_package=ETF-EU-MVP24_FRESH_GENERATION_RENDERER_INTEGRATION
reference_architecture_repo=market-predictions/weekly-etf
source_of_truth_repo=market-predictions/weekly-etf-eu
upstream_pattern_adapted=weekly-etf package-readiness/pre-send validation concept; adapted for EU fresh package readiness without delivery authority
port_behavior_not_us_assumptions=true
us_assumptions_copied=false
fresh_package_readiness_gate_contract_created=true
fresh_package_readiness_gate_contract=control/ETF_EU_FRESH_PACKAGE_READINESS_GATE_CONTRACT_V1.md
fresh_package_readiness_gate_validator_created=true
fresh_package_readiness_gate_validator=tools/validate_etf_eu_fresh_package_readiness_gate.py
fresh_package_readiness_gate_created=true
fresh_package_readiness_gate=output/fresh_generation/etf_eu_fresh_package_readiness_gate_20260710_000000.json
fresh_package_readiness_gate_passed=true
readiness_gate_blockers=[]
ready_for_controlled_delivery=true
delivery_authorized=false
fresh_generation_package_manifest=output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
fresh_generation_ready_artifact=output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
fresh_generation_dutch_primary_markdown=output/fresh_generation/weekly_etf_eu_review_nl_260710.md
fresh_generation_english_companion_markdown=output/fresh_generation/weekly_etf_eu_review_260710.md
fresh_generation_dutch_primary_html=output/fresh_generation/weekly_etf_eu_review_nl_260710.html
fresh_generation_english_companion_html=output/fresh_generation/weekly_etf_eu_review_260710.html
fresh_generation_dutch_primary_pdf=output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
fresh_generation_english_companion_pdf=output/fresh_generation/weekly_etf_eu_review_260710.pdf
markdown_gate_passed=true
html_gate_passed=true
pdf_gate_passed=true
manifest_gate_passed=true
authority_gate_passed=true
routine_manifest_gate_passed=true
routine_run_manifest_updated=true
routine_run_manifest=output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json
generation_and_delivery_separate=true
send_executed=false
transport_attempted=false
receipt_confirmed_from_new_run=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
readiness_status=fresh_package_readiness_gate_passed_ready_for_delivery_prep
selected_next_package=ETF-EU-MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP
```

## Standing upstream-first reuse rule

Before creating or materially changing any ETF EU task, work package, workflow, runtime script, validator, renderer, delivery step, or control file, first inspect the closest upstream `market-predictions/weekly-etf` implementation.

Record one of:

```text
upstream_pattern_reused=<file or concept>
upstream_pattern_adapted=<file or concept + reason>
upstream_pattern_rejected=<file or concept + EU authority reason>
no_upstream_equivalent_found=<search terms / inspected files>
```

Borrow mature concepts and safeguards. Do not port U.S. portfolio state, U.S. holdings, U.S. instruments, U.S. recipient authority, or U.S. delivery assumptions as EU authority.

## Active next package

```text
ETF-EU-MVP26_GUARDED_FRESH_PACKAGE_DELIVERY_PREP
```

## ETF-EU-MVP26 objective

Prepare guarded delivery for the MVP25 readiness-gated fresh package.

The package is eligible for delivery preparation, but delivery is **not authorized** yet:

```text
ready_for_controlled_delivery=true
delivery_authorized=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
```

MVP26 should create the guarded delivery-prep layer around:

```text
output/fresh_generation/weekly_etf_eu_review_nl_260710.md
output/fresh_generation/weekly_etf_eu_review_260710.md
output/fresh_generation/weekly_etf_eu_review_nl_260710.html
output/fresh_generation/weekly_etf_eu_review_260710.html
output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf
output/fresh_generation/weekly_etf_eu_review_260710.pdf
output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json
output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json
output/fresh_generation/etf_eu_fresh_package_readiness_gate_20260710_000000.json
```

Do not send by default.

## Required start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md
control/ETF_EU_FRESH_PACKAGE_READINESS_GATE_CONTRACT_V1.md
control/decisions/ETF_EU_UPSTREAM_FIRST_REUSE_RULE_DECISION_20260710.md
control/decisions/ETF_EU_MVP25_FRESH_PACKAGE_READINESS_GATE_DECISION_20260710.md
```

Then inspect closest upstream `weekly-etf` guarded-delivery and delivery-manifest patterns before modifying anything:

```text
market-predictions/weekly-etf:send_report_runtime_html.py
market-predictions/weekly-etf:send_report.py
market-predictions/weekly-etf:tools/write_etf_delivery_manifest_summary.py
market-predictions/weekly-etf:tools/write_weekly_etf_run_manifest.py
market-predictions/weekly-etf:tools/validate_etf_manifest_evidence.py
```

## MVP26 recommended scope

```text
1. Prepare an explicit fresh-package delivery-prep contract.
2. Confirm package readiness gate is passed.
3. Confirm delivery_authorized=false until explicit user instruction.
4. Create guarded delivery-prep artifact and/or workflow inputs for a future controlled send.
5. Keep actual transport separate unless the user explicitly authorizes sending.
```

## Guardrail

No workflow dispatch, email sending, live delivery, portfolio mutation, valuation-grade promotion, funding authority promotion, production-delivery claim, or receipt confirmation should be started from this state update alone.
